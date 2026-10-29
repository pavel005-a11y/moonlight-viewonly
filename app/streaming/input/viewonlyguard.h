#pragma once

// Client-side safety boundary for Moonlight View Only.
//
// Intercept every outgoing Limelight input call in the SDL input sources.
// This also covers synthetic events from touch timers, gamepad mouse emulation,
// clipboard paste, controller arrivals and cleanup paths.
#include <QtGlobal>

namespace ViewOnlyGuard {

inline bool enabled()
{
    // The command-line flag is translated into this environment variable
    // before application startup, so caching is safe for this process.
    static const bool viewOnly = qEnvironmentVariableIsSet("MOONLIGHT_VIEW_ONLY");
    return viewOnly;
}

template <typename Function, typename... Args>
inline void send(Function function, Args... args)
{
    if (!enabled()) {
        function(args...);
    }
}

} // namespace ViewOnlyGuard
