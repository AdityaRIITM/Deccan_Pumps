from flask import Flask, request, jsonify
from math import log, pow # Using log for natural logarithm (LN) and pow for exponents
from flask_cors import CORS # To handle Cross-Origin Resource Sharing

app = Flask(__name__)
CORS(app) # This allows your frontend (running on file:// or http://localhost:PORT) to talk to this backend.

@app.route('/calculate', methods=['POST'])
def calculate_efficiencies():
    try:
        data = request.get_json()

        # Extracting inputs from the request
        c5_selected_unit = data.get('C5') # SELECTED UNIT FOR FLOW (1, 2, 3, 4)
        c6_pump_flow_value = data.get('C6') # PUMP FLOW VALUE
        f5_specific_speed = data.get('F5') # SPECIFIC Speed
        f6_pump_type = data.get('F6') # Pump type (A, B, C, F, G, J, V)

        # --- F4: PUMP FLOW IN M3/S Calculation ---
        f4_pump_flow_m3s = 0.0
        if c5_selected_unit == 1:
            f4_pump_flow_m3s = c6_pump_flow_value
        elif c5_selected_unit == 2:
            f4_pump_flow_m3s = c6_pump_flow_value / 60000
        elif c5_selected_unit == 3:
            f4_pump_flow_m3s = c6_pump_flow_value / 1000
        elif c5_selected_unit == 4:
            f4_pump_flow_m3s = c6_pump_flow_value * 0.00006309
        else:
            return jsonify({'error': 'Invalid Unit for Flow (C5)'}), 400

        # Ensure F4 is positive for LN calculations
        if f4_pump_flow_m3s <= 0:
            return jsonify({'error': 'Pump Flow (F4) must be greater than zero for calculations.'}), 400

        # --- F9: Efficiency at Optimum Calculation ---
        f9_efficiency_optimum = 0.0
        ln_f4 = log(f4_pump_flow_m3s) # Natural logarithm of F4

        if f6_pump_type == "A":
            f9_efficiency_optimum = 85.134 + 3.85 * ln_f4 - 1.152 * pow(ln_f4, 2)
        elif f6_pump_type in ["B", "C"]:
            f9_efficiency_optimum = 87.6345 + 2.0326 * ln_f4 - 1.4278 * pow(ln_f4, 2)
        elif f6_pump_type == "F":
            f9_efficiency_optimum = 85.778 - 2.219 * ln_f4 - 1.481 * pow(ln_f4, 2)
        elif f6_pump_type == "G":
            f9_efficiency_optimum = 88.365 + 1.701 * ln_f4 - 0.367 * pow(ln_f4, 2)
        elif f6_pump_type == "J":
            f9_efficiency_optimum = 90.466 + 1.074 * ln_f4 - 0.446 * pow(ln_f4, 2)
        elif f6_pump_type == "V":
            f9_efficiency_optimum = 89.575 + 1.102 * ln_f4 - 0.539 * pow(ln_f4, 2)
        else:
            return jsonify({'error': 'Invalid Pump Type (F6)'}), 400

        # --- F10: Efficiency Correction Calculation ---
        f10_efficiency_correction = 0.0
        if f6_pump_type == "V":
            if f5_specific_speed <= 100:
                f10_efficiency_correction = (0.00000001875 * pow(f5_specific_speed, 4) -
                                             0.00001219 * pow(f5_specific_speed, 3) +
                                             0.002517 * pow(f5_specific_speed, 2) -
                                             0.2123 * f5_specific_speed + 6.4316)
            else: # F5 > 100
                f10_efficiency_correction = (0.0000000006184 * pow(f5_specific_speed, 4) -
                                             0.0000007899 * pow(f5_specific_speed, 3) +
                                             0.0003441 * pow(f5_specific_speed, 2) -
                                             0.0471 * f5_specific_speed + 2.0453)
        else: # F6 is not "V"
            if f5_specific_speed < 30:
                f10_efficiency_correction = (-0.0002692 * pow(f5_specific_speed, 3) +
                                             0.02558 * pow(f5_specific_speed, 2) -
                                             0.9566 * f5_specific_speed + 13.717)
            elif f5_specific_speed <= 90:
                f10_efficiency_correction = (-0.00002077 * pow(f5_specific_speed, 3) +
                                             0.004611 * pow(f5_specific_speed, 2) -
                                             0.3076 * f5_specific_speed + 6.452)
            else: # F5 > 90
                f10_efficiency_correction = (0.0000471 * pow(f5_specific_speed, 2) +
                                             0.01879 * f5_specific_speed - 0.9191)

        # --- F11: Efficiency Deviation Calculation ---
        f11_efficiency_deviation = 0.0
        if f4_pump_flow_m3s <= 0.05:
            f11_efficiency_deviation = (19907642.3 * pow(f4_pump_flow_m3s, 4) -
                                        2287352.57 * pow(f4_pump_flow_m3s, 3) +
                                        90466.93 * pow(f4_pump_flow_m3s, 2) -
                                        1521.98 * f4_pump_flow_m3s + 16.6181)
        elif f4_pump_flow_m3s <= 0.9:
            f11_efficiency_deviation = (56.5767 * pow(f4_pump_flow_m3s, 4) -
                                        120.2869 * pow(f4_pump_flow_m3s, 3) +
                                        89.0594 * pow(f4_pump_flow_m3s, 2) -
                                        28.54 * f4_pump_flow_m3s + 6.008)
        elif: f4_pump_flow_m3s <= 10:
            f11_efficiency_deviation = (0.0003773 * pow(f4_pump_flow_m3s, 4) -
                                        0.0105409 * pow(f4_pump_flow_m3s, 3) +
                                        0.111228 * pow(f4_pump_flow_m3s, 2) -
                                        0.55649 * f4_pump_flow_m3s + 2.2392)
        else:
                        f11_efficiency_deviation =1.03

        # --- F12: Actual Efficiency Calculation & Formatting ---
        # The TEXT function in Excel handles formatting and concatenation.
        # We'll calculate the raw value and format it as a string in Python.
        raw_actual_efficiency = f9_efficiency_optimum - f10_efficiency_correction
        
        # This matches the Excel formula's string output: "XX.YY ± ZZ.WW %"
        f12_actual_efficiency_text = f"{raw_actual_efficiency:.2f} &plusmn; {f11_efficiency_deviation:.2f} %"


        # Return results as JSON
        return jsonify({
            'efficiencyOptimum': f9_efficiency_optimum,
            'efficiencyCorrection': f10_efficiency_correction,
            'efficiencyDeviation': f11_efficiency_deviation,
            'actualEfficiency': f12_actual_efficiency_text # Send as pre-formatted string for innerHTML
        })

    except Exception as e:
        # Catch any errors during processing and return a JSON error message
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
