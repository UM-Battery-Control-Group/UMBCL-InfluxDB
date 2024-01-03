STORED_FIELD_NAMES = ["Cycle Index", "Step Index", "Step Type", "Time", "Total Time",
                        "Timestamp(epoch)", "Current(A)", "Voltage(V)", "Capacity(Ah)",
                        "Chg. Cap.(Ah)", "DChg. Cap.(Ah)", "Energy(Wh)", "Chg. Energy(Wh)",
                        "DChg. Energy(Wh)", "Date", "Power(W)", "dQ/dV(mAh/V)", "dQm/dV(mAh/V.g)",
                        "Contact resistance(mΩ)", "Cell Temperature (C)", "Ambient Temperature (C)"]


ARBIN_FIELD_NAMES = ["cycle_index", "step_index", "", "step_time", "test_time", "date_time",
                     "current", "voltage", "", "charge_capacity", "discharge_capacity", "",
                     "charge_energy", "discharge_energy", "", "", "", "", "internal_resistance", "", ""]


NEWARE_VDF_FIELD_NAMES = ["", "", "", "Test Time (second)", "", "Timestamp (epoch)", "Current (amp)", "Potential (volt)",
                          "", "", "", "", "", "", "", "", "", "", "", "", "Ambient Temperature (celsius)"]

NEWARE_FIELD_NAMES = ["Cycle Index", "Step Index", "Step Type", "Time", "Total Time", "", "Current(A)", "Voltage(V)",
                      "Capacity(Ah)", "Chg. Cap.(Ah)", "DChg. Cap.(Ah)", "Energy(Wh)", "Chg. Energy(Wh)",
                      "DChg. Energy(Wh)", "Date", "Power(W)", "dQ/dV(mAh/V)", "dQm/dV(mAh/V.g)", "Contact resistance(mΩ)",
                      "T1(℃)", ""]

BIOLOGIC_FIELD_NAMES = ["cycle number", "", "mode", "", "time/s", "", "I", "Ecell/V", "Capacity/mA.h",
                        "Q charge/mA.h", "Q discharge/mA.h", "", "Energy charge/W.h", "Energy discharge/W.h",
                        "", "", "", "half cycle", "", "Temperature/°C", "Efficiency/%"]
