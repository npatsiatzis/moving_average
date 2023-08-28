// Verilator Example
#include <stdlib.h>
#include <iostream>
#include <cstdlib>
#include <memory>
#include <vector>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include "Vmoving_average.h"
#include "Vmoving_average_moving_average.h"   //to get parameter values, after they've been made visible in SV


#define POSEDGE(ns, period, phase) \
    ((ns) % (period) == (phase))

#define NEGEDGE(ns, period, phase) \
    ((ns) % (period) == ((phase) + (period)) / 2 % (period))

#define CLK_A_PERIOD 30
#define CLK_A_PHASE 0


#define MAX_SIM_TIME 300
#define VERIF_START_TIME 2*CLK_A_PERIOD
vluint64_t sim_time = 0;
vluint64_t posedge_cnt = 0;

// input interface transaction item class
class InTx {
    private:
    public:
        int i_ce;
        int i_sample;
};


// output interface transaction item class
class OutTx {
    public:
        int o_result;
};

//in domain Coverage
class InCoverage{
    private:
        std::set <int> in_cvg;
    
    public:
        void write_coverage(InTx *tx){
            in_cvg.insert(tx->i_sample);
        }

        bool is_covered(int A){            
            return in_cvg.find(A) == in_cvg.end();
        }
};

//out domain Coverage
class OutCoverage {
    private:
        std::set <int> coverage;
        int cvg_size = 0;

    public:
        void write_coverage(OutTx* tx){
            coverage.insert(tx->o_result);
            cvg_size++;
        }

        bool is_full_coverage(){
            return cvg_size == (1 << (Vmoving_average_moving_average::G_I_W))-1;
            // return coverage.size() == (1 << (Vmoving_average_moving_average::G_I_W));
        }
};


// ALU scoreboard
class Scb {
    private:
        // std::deque<InTx*> in_q;
        // std::deque<OutTx*> out_q;
        std::vector<int> in_vec;
        std::vector<int> out_vec;

        // Function to slice a given vector
        // from range X to Y
        int slice_and_ma(std::vector<int>& arr,
                            int X, int Y)
        {
         
            // Starting and Ending iterators
            auto start = arr.begin() + X;
            auto end = arr.begin() + Y + 1;
         
            // To store the sliced vector
            std::vector<int> result(Y - X + 1);
         
            // Copy vector using copy function()
            copy(start, end, result.begin());
         
            // // Return the final sliced vector
            // return result;
            int ma_sum = 0;
            int ma_result = 0;

            for (auto i = result.begin(); i != result.end(); i++){
                ma_sum += *i;
            }
            ma_result = ma_sum / (1 << Vmoving_average_moving_average::G_M_W);
            return ma_result;
        }

    public:
        // Input interface monitor port
        void writeIn(InTx *tx){
            // Push the received transaction item into a queue for later
            // in_q.push_back(tx);
            in_vec.push_back(tx->i_sample);
            delete tx;
        }

        // Output interface monitor port
        void writeOut(OutTx *tx){
            // Push the received transaction item into a queue for later
            // out_q.push_back(tx);
            out_vec.push_back(tx->o_result);
            delete tx;
        }

        void checkPhase(){
            int expected_result = 0;
            for (int i = (1 << Vmoving_average_moving_average::G_M_W); i<out_vec.size()-1; i++) {
                expected_result = slice_and_ma(in_vec,i - (1 << Vmoving_average_moving_average::G_M_W)+1, i);

                if(expected_result != out_vec[i]){
                    std::cout << "Test Failure!" << std::endl;
                    std::cout << "Expected : " <<  expected_result << std::endl;
                    std::cout << "Got : " << out_vec[i] << std::endl;
                    exit(1);
                } else {
                    std::cout << "Test PASS!" << std::endl;
                    std::cout << "Expected : " <<  expected_result << std::endl;
                    std::cout << "Got : " << out_vec[i] << std::endl;   
                }
            }
        }

};

// interface driver
class InDrv {
    private:
        // Vmoving_average *dut;
        std::shared_ptr<Vmoving_average> dut;
        int state;
    public:
        InDrv(std::shared_ptr<Vmoving_average> dut){
            this->dut = dut;
            state = 0;
        }

        void drive(InTx *tx, int & new_tx_ready,int is_a_pos){

            // Don't drive anything if a transaction item doesn't exist


            if(tx != NULL && is_a_pos == 1){
                dut->i_ce = 1;
                dut->i_sample = tx->i_sample;

                new_tx_ready = 1;
                delete tx;
            }

        }
};

// input interface monitor
class InMon {
    private:
        // Vmoving_average *dut;
        std::shared_ptr<Vmoving_average> dut;
        // Scb *scb;
        std::shared_ptr<Scb>  scb;
        // InCoverage *cvg;
        std::shared_ptr<InCoverage> cvg;
    public:
        InMon(std::shared_ptr<Vmoving_average> dut, std::shared_ptr<Scb>  scb, std::shared_ptr<InCoverage> cvg){
            this->dut = dut;
            this->scb = scb;
            this->cvg = cvg;
        }

        void monitor(int is_a_pos){
            // if(dut->i_valid == 1){
            if(is_a_pos ==1 && dut->i_ce == 1) {
                InTx *tx = new InTx();
                tx->i_sample = dut->i_sample;
                // then pass the transaction item to the scoreboard
                scb->writeIn(tx);
                cvg->write_coverage(tx);
            }
        }
};

// ALU output interface monitor
class OutMon {
    private:
        // Vmoving_average *dut;
        std::shared_ptr<Vmoving_average> dut;
        // Scb *scb;
        std::shared_ptr<Scb> scb;
        // OutCoverage *cvg;
        std::shared_ptr<OutCoverage> cvg;
        int state;
    public:
        OutMon(std::shared_ptr<Vmoving_average> dut, std::shared_ptr<Scb> scb, std::shared_ptr<OutCoverage> cvg){
            this->dut = dut;
            this->scb = scb;
            this->cvg = cvg;
            state = 0;
        }

        void monitor(int is_a_pos){


            switch(state) {
                case 0:
                    if(is_a_pos == 1 && dut->i_ce == 1) {
                        state = 1;
                     }

                    break;
                case 1:
                    if(is_a_pos == 1 && dut->i_ce == 1) {
                        state = 2;
                    }
                    break;
                case 2:
                    if(is_a_pos == 1 && dut->i_ce == 1) {
                        state = 3;
                    }
                    break;
                case 3: 
                    if(is_a_pos == 1 && dut->i_ce == 1) {
                        state = 3;
                        OutTx *tx = new OutTx();
                        tx->o_result = dut->o_result;

                        // then pass the transaction item to the scoreboard
                        scb->writeOut(tx);
                        cvg->write_coverage(tx);
                    }
                    break;
                default:
                    state = 0;
            }
        }
};

//sequence (transaction generator)
// coverage-driven random transaction generator
// This will allocate memory for an InTx
// transaction item, randomise the data, until it gets
// input values that have yet to be covered and
// return a pointer to the transaction item object
class Sequence{
    private:
        InTx* in;
        // InCoverage *cvg;
        std::shared_ptr<InCoverage> cvg;
    public:
        Sequence(std::shared_ptr<InCoverage> cvg){
            this->cvg = cvg;
        }

        InTx* genTx(int & new_tx_ready){
            in = new InTx();
            // std::shared_ptr<InTx> in(new InTx());
            if(new_tx_ready == 1){
                in->i_sample = rand() % (1 << (Vmoving_average_moving_average::G_I_W -1));   

                while(cvg->is_covered(in->i_sample) == false){
                    in->i_sample = rand() % (1 << (Vmoving_average_moving_average::G_I_W -1));  

                }
                return in;
            } else {
                return NULL;
            }
        }
};


void dut_reset (std::shared_ptr<Vmoving_average> dut, vluint64_t &sim_time){
    dut->i_rst = 0;
    if(sim_time >= 0 && sim_time < VERIF_START_TIME-1){
        dut->i_rst = 1;
    }
}

void simulation_eval(std::shared_ptr<Vmoving_average> dut,VerilatedVcdC *m_trace, vluint64_t & ns)
{
    dut->eval();
    m_trace->dump(ns);
}

void simulation_tick_posedge(std::shared_ptr<Vmoving_average> dut)
{   
    dut->i_clk = 1;
    
}

void simulation_tick_negedge(std::shared_ptr<Vmoving_average> dut)
{
    dut->i_clk = 0;
    
}


int main(int argc, char** argv, char** env) {
    srand (time(NULL));
    Verilated::commandArgs(argc, argv);
    // Vmoving_average *dut = new Vmoving_average;
    std::shared_ptr<Vmoving_average> dut(new Vmoving_average);

    Verilated::traceEverOn(true);
    VerilatedVcdC *m_trace = new VerilatedVcdC;
    dut->trace(m_trace, 5);
    m_trace->open("waveform.vcd");

    InTx   *tx;
    int new_tx_ready = 1;

    // Here we create the driver, scoreboard, input and output monitor and coverage blocks
    std::unique_ptr<InDrv> drv(new InDrv(dut));
    std::shared_ptr<Scb> scb(new Scb());
    std::shared_ptr<InCoverage> inCoverage(new InCoverage());
    std::shared_ptr<OutCoverage> outCoverage(new OutCoverage());
    std::unique_ptr<InMon> inMon(new InMon(dut,scb,inCoverage));
    std::unique_ptr<OutMon> outMon(new OutMon(dut,scb,outCoverage));
    std::unique_ptr<Sequence> sequence(new Sequence(inCoverage));

    while (outCoverage->is_full_coverage() == false) {
    // while(sim_time < MAX_SIM_TIME*20) {

        dut_reset(dut,sim_time);
        

        if (POSEDGE(sim_time, CLK_A_PERIOD, CLK_A_PHASE)) {
                simulation_tick_posedge(dut);
        }
        if (NEGEDGE(sim_time, CLK_A_PERIOD, CLK_A_PHASE)) {
                simulation_tick_negedge(dut);
        }
        
        simulation_eval(dut, m_trace, sim_time);


        if (sim_time >= VERIF_START_TIME) {
            // Generate a randomised transaction item 
            tx = sequence->genTx(new_tx_ready);
            // Pass the generated transaction item in the driver
            //to convert it to pin wiggles
            //operation similar to than of a connection between
            //a sequencer and a driver in a UVM tb
            drv->drive(tx,new_tx_ready,POSEDGE(sim_time, CLK_A_PERIOD, CLK_A_PHASE));
            // Monitor the input interface
            // also writes recovered transaction to
            // input coverage and scoreboard
            inMon->monitor(POSEDGE(sim_time, CLK_A_PERIOD, CLK_A_PHASE));
            // Monitor the output interface
            // also writes recovered result (out transaction) to
            // output coverage and scoreboard 
            outMon->monitor(POSEDGE(sim_time, CLK_A_PERIOD, CLK_A_PHASE));
        }
        sim_time++;
    }
    scb->checkPhase();
    m_trace->close();  
    exit(EXIT_SUCCESS);
}
