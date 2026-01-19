"""
Flask Web Interface for Map Poster Generator
"""
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import sys
import json
import threading
import uuid
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'maptoposter-secret-key'

# Directories
THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"

# Store generation status
generation_status = {}

def get_available_themes():
    """Get list of available themes with metadata."""
    themes = []
    if os.path.exists(THEMES_DIR):
        for file in sorted(os.listdir(THEMES_DIR)):
            if file.endswith('.json'):
                theme_name = file[:-5]
                theme_path = os.path.join(THEMES_DIR, file)
                try:
                    with open(theme_path, 'r') as f:
                        data = json.load(f)
                        themes.append({
                            'id': theme_name,
                            'name': data.get('name', theme_name),
                            'description': data.get('description', ''),
                            'bg': data.get('bg', '#FFFFFF'),
                            'text': data.get('text', '#000000')
                        })
                except:
                    themes.append({
                        'id': theme_name,
                        'name': theme_name,
                        'description': '',
                        'bg': '#FFFFFF',
                        'text': '#000000'
                    })
    return themes

def generate_poster_async(job_id, city, country, theme, distance):
    """Generate poster in background thread."""
    try:
        generation_status[job_id] = {'status': 'processing', 'message': 'Starting generation...'}
        
        # Import here to avoid circular imports
        import osmnx as ox
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        from matplotlib.font_manager import FontProperties
        import matplotlib.colors as mcolors
        import numpy as np
        from geopy.geocoders import Nominatim
        import time
        
        generation_status[job_id]['message'] = 'Looking up coordinates...'
        
        # Get coordinates
        geolocator = Nominatim(user_agent="city_map_poster_web")
        time.sleep(1)
        location = geolocator.geocode(f"{city}, {country}")
        
        if not location:
            generation_status[job_id] = {'status': 'error', 'message': f'Could not find {city}, {country}'}
            return
        
        point = (location.latitude, location.longitude)
        generation_status[job_id]['message'] = 'Downloading street network...'
        
        # Load theme
        theme_file = os.path.join(THEMES_DIR, f"{theme}.json")
        with open(theme_file, 'r') as f:
            THEME = json.load(f)
        
        # Load fonts
        fonts = {
            'bold': os.path.join(FONTS_DIR, 'Roboto-Bold.ttf'),
            'regular': os.path.join(FONTS_DIR, 'Roboto-Regular.ttf'),
            'light': os.path.join(FONTS_DIR, 'Roboto-Light.ttf'),
            'modern': os.path.join(FONTS_DIR, 'Montserrat-Bold.ttf')
        }
        
        # Fetch data
        G = ox.graph_from_point(point, dist=distance, dist_type='bbox', network_type='all')
        
        generation_status[job_id]['message'] = 'Downloading water features...'
        try:
            water = ox.features_from_point(point, tags={'natural': 'water', 'waterway': 'riverbank'}, dist=distance)
        except:
            water = None
        
        generation_status[job_id]['message'] = 'Downloading parks...'
        try:
            parks = ox.features_from_point(point, tags={'leisure': 'park', 'landuse': 'grass'}, dist=distance)
        except:
            parks = None
        
        generation_status[job_id]['message'] = 'Rendering map...'
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 16), facecolor=THEME['bg'])
        ax.set_facecolor(THEME['bg'])
        ax.set_position([0, 0, 1, 1])
        
        # Plot layers
        if water is not None and not water.empty:
            water.plot(ax=ax, facecolor=THEME['water'], edgecolor='none', zorder=1)
        if parks is not None and not parks.empty:
            parks.plot(ax=ax, facecolor=THEME['parks'], edgecolor='none', zorder=2)
        
        # Road colors and widths
        edge_colors = []
        edge_widths = []
        for u, v, data in G.edges(data=True):
            highway = data.get('highway', 'unclassified')
            if isinstance(highway, list):
                highway = highway[0] if highway else 'unclassified'
            
            if highway in ['motorway', 'motorway_link']:
                color = THEME['road_motorway']
                width = 1.2
            elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
                color = THEME['road_primary']
                width = 1.0
            elif highway in ['secondary', 'secondary_link']:
                color = THEME['road_secondary']
                width = 0.8
            elif highway in ['tertiary', 'tertiary_link']:
                color = THEME['road_tertiary']
                width = 0.6
            elif highway in ['residential', 'living_street', 'unclassified']:
                color = THEME['road_residential']
                width = 0.4
            else:
                color = THEME['road_default']
                width = 0.4
            
            edge_colors.append(color)
            edge_widths.append(width)
        
        ox.plot_graph(G, ax=ax, bgcolor=THEME['bg'], node_size=0,
                      edge_color=edge_colors, edge_linewidth=edge_widths,
                      show=False, close=False)
        
        # Gradient fades
        def create_gradient_fade(ax, color, location='bottom', zorder=10):
            vals = np.linspace(0, 1, 256).reshape(-1, 1)
            gradient = np.hstack((vals, vals))
            rgb = mcolors.to_rgb(color)
            my_colors = np.zeros((256, 4))
            my_colors[:, 0] = rgb[0]
            my_colors[:, 1] = rgb[1]
            my_colors[:, 2] = rgb[2]
            if location == 'bottom':
                my_colors[:, 3] = np.linspace(1, 0, 256)
                extent_y_start = 0
                extent_y_end = 0.25
            else:
                my_colors[:, 3] = np.linspace(0, 1, 256)
                extent_y_start = 0.75
                extent_y_end = 1.0
            custom_cmap = mcolors.ListedColormap(my_colors)
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            y_range = ylim[1] - ylim[0]
            y_bottom = ylim[0] + y_range * extent_y_start
            y_top = ylim[0] + y_range * extent_y_end
            ax.imshow(gradient, extent=[xlim[0], xlim[1], y_bottom, y_top],
                      aspect='auto', cmap=custom_cmap, zorder=zorder, origin='lower')
        
        create_gradient_fade(ax, THEME['gradient_color'], location='bottom', zorder=10)
        create_gradient_fade(ax, THEME['gradient_color'], location='top', zorder=10)
        
        # Typography
        if os.path.exists(fonts['modern']):
            font_main = FontProperties(fname=fonts['modern'], size=60)
        else:
            font_main = FontProperties(fname=fonts['bold'], size=60)
        font_sub = FontProperties(fname=fonts['light'], size=22)
        font_coords = FontProperties(fname=fonts['regular'], size=14)
        font_attr = FontProperties(fname=fonts['light'], size=8)
        
        spaced_city = "  ".join(list(city.upper()))
        
        ax.text(0.5, 0.14, spaced_city, transform=ax.transAxes,
                color=THEME['text'], ha='center', fontproperties=font_main, zorder=11)
        ax.text(0.5, 0.10, country.upper(), transform=ax.transAxes,
                color=THEME['text'], ha='center', fontproperties=font_sub, zorder=11)
        
        lat, lon = point
        coords = f"{lat:.4f}° N / {lon:.4f}° E" if lat >= 0 else f"{abs(lat):.4f}° S / {lon:.4f}° E"
        if lon < 0:
            coords = coords.replace("E", "W")
        
        ax.text(0.5, 0.07, coords, transform=ax.transAxes,
                color=THEME['text'], alpha=0.7, ha='center', fontproperties=font_coords, zorder=11)
        ax.plot([0.4, 0.6], [0.125, 0.125], transform=ax.transAxes,
                color=THEME['text'], linewidth=1, zorder=11)
        ax.text(0.98, 0.02, "© OpenStreetMap contributors", transform=ax.transAxes,
                color=THEME['text'], alpha=0.5, ha='right', va='bottom',
                fontproperties=font_attr, zorder=11)
        
        # Save
        generation_status[job_id]['message'] = 'Saving poster...'
        if not os.path.exists(POSTERS_DIR):
            os.makedirs(POSTERS_DIR)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        city_slug = city.lower().replace(' ', '_')
        filename = f"{city_slug}_{theme}_{timestamp}.png"
        output_path = os.path.join(POSTERS_DIR, filename)
        
        plt.savefig(output_path, dpi=300, facecolor=THEME['bg'])
        plt.close()
        
        generation_status[job_id] = {
            'status': 'complete',
            'message': 'Poster generated successfully!',
            'filename': filename
        }
        
    except Exception as e:
        generation_status[job_id] = {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    """Main page."""
    themes = get_available_themes()
    return render_template('index.html', themes=themes)

@app.route('/api/themes')
def api_themes():
    """Get available themes."""
    return jsonify(get_available_themes())

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Start poster generation."""
    data = request.json
    city = data.get('city', '').strip()
    country = data.get('country', '').strip()
    theme = data.get('theme', 'feature_based')
    distance = int(data.get('distance', 12000))
    
    if not city or not country:
        return jsonify({'error': 'City and country are required'}), 400
    
    # Create job
    job_id = str(uuid.uuid4())
    generation_status[job_id] = {'status': 'queued', 'message': 'Job queued...'}
    
    # Start background thread
    thread = threading.Thread(target=generate_poster_async, args=(job_id, city, country, theme, distance))
    thread.start()
    
    return jsonify({'job_id': job_id})

@app.route('/api/status/<job_id>')
def api_status(job_id):
    """Check generation status."""
    status = generation_status.get(job_id, {'status': 'not_found', 'message': 'Job not found'})
    return jsonify(status)

@app.route('/posters/<filename>')
def serve_poster(filename):
    """Serve generated poster."""
    return send_from_directory(POSTERS_DIR, filename)

@app.route('/api/posters')
def api_posters():
    """List generated posters."""
    posters = []
    if os.path.exists(POSTERS_DIR):
        for f in sorted(os.listdir(POSTERS_DIR), reverse=True):
            if f.endswith('.png'):
                posters.append({
                    'filename': f,
                    'url': f'/posters/{f}'
                })
    return jsonify(posters[:20])  # Return last 20

if __name__ == '__main__':
    print("=" * 50)
    print("Map Poster Generator - Web Interface")
    print("=" * 50)
    print("\nOpen http://localhost:5000 in your browser\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
