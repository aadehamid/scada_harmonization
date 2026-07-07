# sparkplug (pipeline layer 4 — Phase 2)

Maps PLC-facing values to Sparkplug B (group/node/device IDs, metric names, aliases,
datatypes) and publishes to the per-site Mosquitto broker — births (NBIRTH/DBIRTH), NDATA,
lifecycle, per the Sparkplug B 3.0 contract. Library choice pending Phase 2 acceptance test
(pysparkplug is a *candidate* — charter §4.1). No code until Phase 2.
