import streamlit as st
import folium
import json
from streamlit_folium import folium_static

# Senegal regions with approximate coordinates for centroids
SENEGAL_REGIONS = {
    "Dakar": {"coords": [14.7167, -17.4677]},
    "Diourbel": {"coords": [14.6667, -16.2333]},
    "Fatick": {"coords": [14.3333, -16.4167]},
    "Kaffrine": {"coords": [14.1067, -15.5506]},
    "Kaolack": {"coords": [14.1500, -16.0833]},
    "Kédougou": {"coords": [12.5600, -12.1750]},
    "Kolda": {"coords": [12.8833, -14.9500]},
    "Louga": {"coords": [15.6167, -16.2167]},
    "Matam": {"coords": [15.6558, -13.2553]},
    "Saint-Louis": {"coords": [16.0333, -16.5000]},
    "Sédhiou": {"coords": [12.7081, -15.5569]},
    "Tambacounda": {"coords": [13.7667, -13.6667]},
    "Thiès": {"coords": [14.7886, -16.9260]},
    "Ziguinchor": {"coords": [12.5833, -16.2667]}
}

# Malaria probability matrix (14 regions x 30 time periods)
# Each row represents a region, each column represents a time period
PROBABILITY_MATRIX = [
    [0.9845, 0.2214, 0.2939, 0.3305, 0.3406, 0.7114, 0.6328, 0.824, 0.3168, 0.4172, 0.4448, 0.8967, 0.0481, 0.6603, 0.0002, 0.2604, 0.2963, 0.1746, 0.7079, 0.6321, 0.9875, 0.7878, 0.4561, 0.1266, 0.9593, 0.6693, 0.4301, 0.8074, 0.1852, 0.5544],
    [0.3653, 0.6439, 0.6074, 0.1077, 0.5932, 0.1036, 0.1623, 0.5674, 0.2763, 0.1712, 0.2757, 0.1772, 0.1297, 0.9872, 0.7849, 0.125, 0.3404, 0.942, 0.6117, 0.7131, 0.0028, 0.7634, 0.649, 0.2931, 0.9216, 0.1493, 0.9551, 0.9081, 0.6372, 0.9331],
    [0.0565, 0.7447, 0.9565, 0.7458, 0.809, 0.5198, 0.6946, 0.9123, 0.1864, 0.7919, 0.2049, 0.9492, 0.7571, 0.8383, 0.2694, 0.2811, 0.2941, 0.5997, 0.9758, 0.54, 0.613, 0.165, 0.6372, 0.7806, 0.9546, 0.3796, 0.4902, 0.5454, 0.6768, 0.1382],
    [0.2359, 0.4021, 0.2361, 0.4413, 0.7912, 0.5451, 0.6601, 0.1692, 0.6778, 0.2769, 0.0908, 0.329, 0.3049, 0.0383, 0.9427, 0.3995, 0.2073, 0.8191, 0.7873, 0.0622, 0.8913, 0.4827, 0.8127, 0.0307, 0.7903, 0.3118, 0.8583, 0.9334, 0.4371, 0.1675],
    [0.4, 0.2288, 0.9549, 0.6188, 0.0371, 0.7653, 0.4445, 0.5809, 0.2089, 0.7354, 0.1815, 0.3012, 0.2945, 0.2498, 0.5945, 0.4841, 0.4034, 0.3691, 0.9891, 0.8072, 0.7759, 0.4052, 0.2809, 0.9315, 0.0287, 0.7858, 0.2408, 0.7372, 0.5714, 0.0176],
    [0.2589, 0.6566, 0.0137, 0.1904, 0.9037, 0.423, 0.5271, 0.7093, 0.0043, 0.6136, 0.1256, 0.2478, 0.6411, 0.7915, 0.4611, 0.4253, 0.9695, 0.9626, 0.5409, 0.6307, 0.2164, 0.8113, 0.6378, 0.6449, 0.2422, 0.4959, 0.7917, 0.8768, 0.5515, 0.0143],
    [0.9865, 0.1289, 0.6939, 0.8896, 0.6197, 0.7052, 0.8652, 0.3157, 0.2084, 0.5997, 0.9325, 0.1088, 0.5999, 0.3796, 0.8164, 0.9264, 0.0044, 0.2317, 0.5559, 0.1151, 0.7276, 0.8171, 0.0437, 0.5705, 0.3337, 0.1961, 0.6668, 0.9401, 0.8124, 0.1188],
    [0.5508, 0.7079, 0.7045, 0.7736, 0.6533, 0.2295, 0.5639, 0.2794, 0.8305, 0.8925, 0.1592, 0.2654, 0.4999, 0.6621, 0.8549, 0.0901, 0.196, 0.2765, 0.4369, 0.7481, 0.1308, 0.3528, 0.7411, 0.8491, 0.6658, 0.9515, 0.2982, 0.6144, 0.19, 0.3748],
    [0.5198, 0.9807, 0.253, 0.933, 0.706, 0.6988, 0.772, 0.1583, 0.9362, 0.5653, 0.0615, 0.0203, 0.3151, 0.3275, 0.1164, 0.4112, 0.5159, 0.611, 0.1711, 0.0734, 0.687, 0.652, 0.1494, 0.9234, 0.2788, 0.9985, 0.4224, 0.921, 0.2074, 0.825],
    [0.0864, 0.1508, 0.1115, 0.8772, 0.2002, 0.4522, 0.7008, 0.9375, 0.8679, 0.9823, 0.7208, 0.6976, 0.1108, 0.2875, 0.4309, 0.1725, 0.2298, 0.15, 0.2593, 0.9428, 0.8474, 0.3475, 0.7742, 0.8009, 0.9595, 0.6373, 0.0769, 0.8859, 0.5248, 0.6779],
    [0.4022, 0.5446, 0.5243, 0.4991, 0.6904, 0.3969, 0.2624, 0.6156, 0.7699, 0.6951, 0.6405, 0.9725, 0.4082, 0.7383, 0.7088, 0.4154, 0.3637, 0.8278, 0.8809, 0.4362, 0.3305, 0.6924, 0.2242, 0.0951, 0.5572, 0.2275, 0.2912, 0.5246, 0.9361, 0.5293],
    [0.8336, 0.3215, 0.8116, 0.5324, 0.7701, 0.7517, 0.7502, 0.6828, 0.4762, 0.6112, 0.1746, 0.9844, 0.6406, 0.1477, 0.8282, 0.7216, 0.023, 0.5067, 0.8803, 0.7337, 0.6321, 0.2539, 0.0452, 0.3913, 0.2922, 0.1331, 0.559, 0.8666, 0.0955, 0.311],
    [0.2797, 0.1282, 0.5218, 0.2582, 0.8829, 0.4238, 0.4255, 0.2473, 0.9787, 0.6909, 0.6177, 0.3698, 0.382, 0.8957, 0.6227, 0.739, 0.8884, 0.8636, 0.8086, 0.5484, 0.3219, 0.8819, 0.7474, 0.4027, 0.6784, 0.3127, 0.3805, 0.6512, 0.0318, 0.0091],
    [0.8841, 0.1233, 0.843, 0.3332, 0.5702, 0.7067, 0.8711, 0.9014, 0.2361, 0.5046, 0.7993, 0.2273, 0.7937, 0.7474, 0.7306, 0.3866, 0.8968, 0.2646, 0.0342, 0.4652, 0.5977, 0.5881, 0.1687, 0.7433, 0.3471, 0.3327, 0.6004, 0.8888, 0.4878, 0.8117]
]

def get_probabilities_for_time(time_index):
    """Get probability dictionary for all regions at a specific time index"""
    region_names = list(SENEGAL_REGIONS.keys())
    probabilities = {}
    
    for i, region in enumerate(region_names):
        # Convert from 0-1 scale to 0-100 percentage
        probabilities[region] = PROBABILITY_MATRIX[i][time_index] * 100
    
    return probabilities

def get_color(probability):
    """Get color based on malaria probability (0-100)"""
    if probability < 20:
        return '#fee5d9'  # Very light red
    elif probability < 40:
        return '#fcae91'  # Light red
    elif probability < 60:
        return '#fb6a4a'  # Medium red
    elif probability < 80:
        return '#de2d26'  # Red
    else:
        return '#a50f15'  # Dark red

def create_map(probabilities):
    """Create a Folium map with color-coded regions"""
    m = folium.Map(
        location=[14.4974, -14.4524],  # Center of Senegal
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    for region, info in SENEGAL_REGIONS.items():
        prob = probabilities.get(region, 0)
        color = get_color(prob)
        
        folium.CircleMarker(
            location=info["coords"],
            radius=25,
            popup=f"<b>{region}</b><br>Malaria Risk: {prob:.1f}%",
            tooltip=f"{region}: {prob:.1f}%",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    return m

def main():
    st.set_page_config(page_title="Senegal Malaria Risk Map", layout="wide")
    
    st.title("🗺️ Senegal Malaria Risk Map")
    st.markdown("Color-coded regional malaria probability visualization over time")
    
    # Get number of time periods from matrix
    num_time_periods = len(PROBABILITY_MATRIX[0])
    
    # Sidebar for time selection
    with st.sidebar:
        st.header("⏰ Time Period Selection")
        
        # Slider to select time period (1 to 30 months)
        time_period = st.slider(
            "Select Month",
            min_value=1,
            max_value=num_time_periods,
            value=1,
            step=1,
            help=f"Select month from 1 to {num_time_periods}"
        )
        
        st.info(f"**Currently Viewing:**\n\nMonth {time_period}")
        
        # Get probabilities for selected time period (subtract 1 for 0-indexing)
        probabilities = get_probabilities_for_time(time_period - 1)
        
        st.markdown("---")
        
        # Display current probabilities
        st.subheader("📊 Regional Probabilities")
        for region in sorted(probabilities.keys()):
            color = get_color(probabilities[region])
            st.markdown(
                f"<div style='padding: 5px; margin: 2px; background-color: {color}; border-radius: 3px;'>"
                f"<b>{region}:</b> {probabilities[region]:.1f}%</div>",
                unsafe_allow_html=True
            )
    
    # Main content - Map display
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"Malaria Risk Map - Month {time_period}")
        m = create_map(probabilities)
        folium_static(m, width=800, height=600)
    
    with col2:
        st.subheader("Risk Legend")
        st.markdown("""
        <div style='background: linear-gradient(to bottom, #a50f15, #de2d26, #fb6a4a, #fcae91, #fee5d9); 
                    height: 200px; width: 50px; border: 1px solid #ccc;'></div>
        <div style='margin-top: 10px;'>
            <b>High Risk (80-100%)</b><br>
            <b>Medium-High (60-80%)</b><br>
            <b>Medium (40-60%)</b><br>
            <b>Low-Medium (20-40%)</b><br>
            <b>Low Risk (0-20%)</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Summary Statistics")
        if probabilities:
            avg_risk = sum(probabilities.values()) / len(probabilities)
            max_region = max(probabilities, key=probabilities.get)
            min_region = min(probabilities, key=probabilities.get)
            
            st.metric("Average Risk", f"{avg_risk:.1f}%")
            st.metric("Highest Risk", f"{max_region}", f"{probabilities[max_region]:.1f}%")
            st.metric("Lowest Risk", f"{min_region}", f"{probabilities[min_region]:.1f}%")
        
        st.markdown("---")
        st.caption(f"Data: 14 regions × 30 time periods")

if __name__ == "__main__":
    main()