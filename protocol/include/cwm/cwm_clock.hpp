// Coordinator clock: all gameplay systems share native turns on one timeline.
#pragma once
#include <algorithm>
#include <chrono>
#include <cmath>
#include <initializer_list>

namespace cdda::cwm {
enum PauseReason : unsigned { Manual = 1, Menu = 2, Threat = 4, Recovery = 8, Decision = 16 };
class SimulationClock {
public:
    using Wall = std::chrono::steady_clock;
    // One effective rate. F8 edits that rate in the current native context.
    // Context preferences are alternatives, never multiplied together.
    void sample(Wall::time_point now, bool running) {
        const bool fast=rest_context_ && scale_>4.;
        if(accelerated_ && (!running || !fast))tick_end_=std::max(tick_end_,elapsed_);
        accelerated_=running && fast;
        if(started_ && running_ && running) {
            const double dt=std::chrono::duration<double>(now-last_).count();
            elapsed_+=std::clamp(dt,0.,.25)*scale_;
        }
        last_=now;started_=true;running_=running;
    }
    void set_rest_context(bool rest) {
        if(rest==rest_context_)return;
        if(rest) {normal_scale_=scale_;scale_=rest_scale_;}
        else {rest_scale_=scale_;scale_=normal_scale_;}
        rest_context_=rest;
        tick_end_=std::max(tick_end_,elapsed_); // Discard unused accelerated credit.
        accelerated_=false;
    }
    bool rest_context() const {return rest_context_;}
    bool set_scale(double value) {
        if(!std::isfinite(value) || value<.25 || value>(rest_context_?4096.:4.))return false;
        if(rest_context_ && value<scale_)tick_end_=std::max(tick_end_,elapsed_);
        scale_=value;
        if(rest_context_)rest_scale_=value;else normal_scale_=value;
        return true;
    }
    bool set_scale(double value,bool expected_rest_context) {
        return expected_rest_context==rest_context_ && set_scale(value);
    }
    static double next_scale(double current,bool rest) {
        if(rest) {for(double value:{1.,4.,64.,256.,1024.,4096.})if(value>current+1e-5)return value;return 1.;}
        for(double value:{.5,1.,2.,4.})if(value>current+1e-5)return value;
        return .5;
    }
    double scale() const { return scale_; }
    double elapsed() const { return elapsed_; }
    bool tick_due() const { return elapsed_ + 1e-8 >= tick_end_; }
    double remaining_work() const { return std::max(0.0, action_due_ - elapsed_); }
    bool action_due() const { return elapsed_ + 1e-8 >= action_due_; }
    // Activity actors already own their native debit; pace exactly that work.
    double charge_work(int moves, int native_speed) {
        const double duration = double(std::max(0, moves)) / std::max(1, native_speed);
        action_due_ = std::max(action_due_, elapsed_) + duration;
        return duration / scale_;
    }
    double charge_action(int moves, int native_speed) {
        const double duration = double(std::max(0, moves)) / std::max(1, native_speed);
        action_due_ = std::max(action_due_, elapsed_) + std::max(0.05, duration);
        return duration / scale_;
    }
    void complete_tick() {
        tick_end_ += 1.0;
        // Keep bounded credit only for deliberate fast rest. Every credit still
        // requires one native world tick; pause/wake discard unused credit.
        if (accelerated_) tick_end_ = std::max(tick_end_, elapsed_ - 32.0);
        else if (tick_due()) tick_end_ = elapsed_ + 1.0;
    }
private:
    Wall::time_point last_{};
    bool started_{false}, running_{false}, accelerated_{false}, rest_context_{false};
    double normal_scale_{1.},rest_scale_{1024.};
    double elapsed_{0.0}, scale_{1.0}, tick_end_{1.0}, action_due_{0.0};
};
}
