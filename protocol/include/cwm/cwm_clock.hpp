// Coordinator clock: all gameplay systems share native turns on one timeline.
#pragma once
#include <algorithm>
#include <chrono>
#include <cmath>

namespace cdda::cwm {
enum PauseReason : unsigned { Manual = 1, Menu = 2, Threat = 4, Recovery = 8, Decision = 16 };
class SimulationClock {
public:
    using Wall = std::chrono::steady_clock;
    void sample(Wall::time_point now, bool running) {
        if (started_ && running_ && running) {
            // Suspend/stalls lose wall time rather than creating catch-up turns.
            const double dt = std::chrono::duration<double>(now - last_).count();
            elapsed_ += std::clamp(dt, 0.0, 0.25) * scale_;
        }
        last_ = now; started_ = true; running_ = running;
    }
    bool set_scale(double value) {
        if (!std::isfinite(value) || value < 0.25 || value > 4.0) return false;
        scale_ = value; return true;
    }
    double scale() const { return scale_; }
    double elapsed() const { return elapsed_; }
    bool tick_due() const { return elapsed_ + 1e-8 >= tick_end_; }
    bool action_due() const { return elapsed_ + 1e-8 >= action_due_; }
    double charge_action(int moves, int native_speed) {
        const double duration = double(std::max(0, moves)) / std::max(1, native_speed);
        action_due_ = std::max(action_due_, elapsed_) + std::max(0.05, duration);
        return duration / scale_;
    }
    void complete_tick() {
        tick_end_ += 1.0;
        if (tick_due()) tick_end_ = elapsed_ + 1.0;
    }
private:
    Wall::time_point last_{};
    bool started_{false}, running_{false};
    double elapsed_{0.0}, scale_{1.0}, tick_end_{1.0}, action_due_{0.0};
};
}
