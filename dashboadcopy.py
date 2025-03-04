import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from flask import Flask, send_from_directory
import os

# Charger les données
df = pd.read_csv(r"C:\Users\moham\Documents\Pokemon_DataAnalysis\data\pokemon_dataset_with_images.csv")

# Filtrer les Pokémon spéciaux (Legendary et Mythical)
df_speciaux = df[df['category'].isin(['legendary', 'mythical', 'ultra beast'])]

# Définir les générations
ancienne_generation = ['gen 1', 'gen 2', 'gen 3']  # Anciennes générations
nouvelle_generation = ['gen 4', 'gen 5', 'gen 6', 'gen 7', 'gen 8', 'gen 9']  # Nouvelles générations

# Séparer les Pokémon spéciaux par génération
df_ancienne = df_speciaux[df_speciaux['generation'].isin(ancienne_generation)]
df_nouvelle = df_speciaux[df_speciaux['generation'].isin(nouvelle_generation)]

# Matrice des avantages/désavantages (exemple simplifié)
type_advantages = {
    'fire': {'grass': 2.0, 'water': 0.5, 'electric': 1.0, 'fire': 0.5},
    'water': {'fire': 2.0, 'grass': 0.5, 'electric': 1.0, 'water': 0.5},
    'grass': {'water': 2.0, 'fire': 0.5, 'electric': 1.0, 'grass': 0.5},
    'electric': {'water': 2.0, 'grass': 1.0, 'fire': 1.0, 'electric': 0.5},
    # Ajoutez d'autres types ici
}

# Fonction pour calculer le multiplicateur de type
def calculate_type_multiplier(attacker_type, defender_type):
    if isinstance(attacker_type, str) and isinstance(defender_type, str):
        return type_advantages.get(attacker_type, {}).get(defender_type, 1.0)
    return 1.0

# Fonction pour calculer les dégâts
def calculate_damage(attacker, defender):
    # Multiplicateur de type pour le type primaire
    multiplier1 = calculate_type_multiplier(attacker['primary_type'].lower(), defender['primary_type'].lower())
    
    # Multiplicateur de type pour le type secondaire (si applicable)
    multiplier2 = 1.0
    if pd.notna(defender['secondary_type']):
        multiplier2 = calculate_type_multiplier(attacker['primary_type'].lower(), defender['secondary_type'].lower())
    
    # Moyenne des multiplicateurs
    total_multiplier = (multiplier1 + multiplier2) / 2

    # Dégâts physiques
    physical_damage = (attacker['attack'] / defender['defense']) * total_multiplier

    # Dégâts spéciaux
    special_damage = (attacker['special_attack'] / defender['special_defense']) * total_multiplier

    # Dégâts totaux (moyenne des dégâts physiques et spéciaux)
    total_damage = (physical_damage + special_damage) / 2
    return total_damage

# Fonction pour déterminer le gagnant
def determine_winner(pokemon1, pokemon2):
    damage1 = calculate_damage(pokemon1, pokemon2)
    damage2 = calculate_damage(pokemon2, pokemon1)

    if damage1 > damage2:
        return f"{pokemon1['name']} de la génération {pokemon1['generation']} gagne ! 🎉"
    elif damage2 > damage1:
        return f"{pokemon2['name']} de la génération {pokemon2['generation']} gagne ! 🎉"
    else:
        return "Match nul ! 🤝"

# Initialiser l'application Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Servir les fichiers image statiques
@server.route('/data/Images/<path:filename>')
def serve_image(filename):
    return send_from_directory('data/Images', filename)

# Fonction pour créer un graphique en radar
def create_radar_chart(pokemon1, pokemon2):
    stats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=pokemon1[stats].values,
        theta=stats,
        fill='toself',
        name=pokemon1['name']
    ))

    fig.add_trace(go.Scatterpolar(
        r=pokemon2[stats].values,
        theta=stats,
        fill='toself',
        name=pokemon2['name']
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title="Comparaison des stats en radar"
    )
    return fig

# Layout du dashboard
app.layout = html.Div([
    html.H1("Simulateur de Combat Pokémon Spéciaux", style={'textAlign': 'center', 'color': '#FFCC00', 'fontFamily': 'Arial'}),
    
    html.Div([
        # Carte du Pokémon de l'ancienne génération
        html.Div([
            html.Img(id='pokemon1-image', src='', style={'width': '150px', 'height': '150px'}),
            html.H3(id='pokemon1-name', style={'textAlign': 'center'}),
            html.P(id='pokemon1-generation', style={'textAlign': 'center'}),  # Ajout de la génération
            html.Ul([
                html.Li(f"HP: {df_ancienne.iloc[0]['hp']}", id='pokemon1-hp'),
                html.Li(f"Attaque: {df_ancienne.iloc[0]['attack']}", id='pokemon1-attack'),
                html.Li(f"Défense: {df_ancienne.iloc[0]['defense']}", id='pokemon1-defense'),
                html.Li(f"Attaque Spéciale: {df_ancienne.iloc[0]['special_attack']}", id='pokemon1-special-attack'),
                html.Li(f"Défense Spéciale: {df_ancienne.iloc[0]['special_defense']}", id='pokemon1-special-defense'),
                html.Li(f"Vitesse: {df_ancienne.iloc[0]['speed']}", id='pokemon1-speed')
            ], style={'listStyleType': 'none', 'padding': '0'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center', 'border': '2px solid #000', 'padding': '10px', 'backgroundColor': '#F8F8F8'}),
        
        # Graphique en radar
        html.Div([
            dcc.Graph(id='radar-chart')
        ], style={'width': '40%', 'display': 'inline-block', 'textAlign': 'center'}),
        
        # Carte du Pokémon de la nouvelle génération
        html.Div([
            html.Img(id='pokemon2-image', src='', style={'width': '150px', 'height': '150px'}),
            html.H3(id='pokemon2-name', style={'textAlign': 'center'}),
            html.P(id='pokemon2-generation', style={'textAlign': 'center'}),  # Ajout de la génération
            html.Ul([
                html.Li(f"HP: {df_nouvelle.iloc[0]['hp']}", id='pokemon2-hp'),
                html.Li(f"Attaque: {df_nouvelle.iloc[0]['attack']}", id='pokemon2-attack'),
                html.Li(f"Défense: {df_nouvelle.iloc[0]['defense']}", id='pokemon2-defense'),
                html.Li(f"Attaque Spéciale: {df_nouvelle.iloc[0]['special_attack']}", id='pokemon2-special-attack'),
                html.Li(f"Défense Spéciale: {df_nouvelle.iloc[0]['special_defense']}", id='pokemon2-special-defense'),
                html.Li(f"Vitesse: {df_nouvelle.iloc[0]['speed']}", id='pokemon2-speed')
            ], style={'listStyleType': 'none', 'padding': '0'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center', 'border': '2px solid #000', 'padding': '10px', 'backgroundColor': '#F8F8F8'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}),
    
    # Résultat du combat
    html.Div(id='combat-result', style={'textAlign': 'center', 'fontSize': '24px', 'marginTop': '20px', 'fontFamily': 'Arial', 'color': '#FF0000'}),
    
    # Dropdowns pour sélectionner les Pokémon
    html.Div([
        html.Label("Choisissez un Pokémon de l'ancienne génération :", style={'fontFamily': 'Arial'}),
        dcc.Dropdown(id='pokemon1', options=[{'label': row['name'], 'value': row['pokemon_id']} for index, row in df_ancienne.iterrows()], value=None, style={'width': '50%', 'margin': 'auto'}),  # Sélection par défaut vide
        
        html.Label("Choisissez un Pokémon de la nouvelle génération :", style={'fontFamily': 'Arial', 'marginTop': '20px'}),
        dcc.Dropdown(id='pokemon2', options=[{'label': row['name'], 'value': row['pokemon_id']} for index, row in df_nouvelle.iterrows()], value=None, style={'width': '50%', 'margin': 'auto'})  # Sélection par défaut vide
    ], style={'textAlign': 'center', 'marginTop': '20px'})
])

# Callback pour mettre à jour les informations des Pokémon et le graphique
@app.callback(
    [Output('pokemon1-image', 'src'),
     Output('pokemon1-name', 'children'),
     Output('pokemon1-generation', 'children'),  # Ajout de la génération
     Output('pokemon1-hp', 'children'),
     Output('pokemon1-attack', 'children'),
     Output('pokemon1-defense', 'children'),
     Output('pokemon1-special-attack', 'children'),
     Output('pokemon1-special-defense', 'children'),
     Output('pokemon1-speed', 'children'),
     Output('pokemon2-image', 'src'),
     Output('pokemon2-name', 'children'),
     Output('pokemon2-generation', 'children'),  # Ajout de la génération
     Output('pokemon2-hp', 'children'),
     Output('pokemon2-attack', 'children'),
     Output('pokemon2-defense', 'children'),
     Output('pokemon2-special-attack', 'children'),
     Output('pokemon2-special-defense', 'children'),
     Output('pokemon2-speed', 'children'),
     Output('radar-chart', 'figure'),
     Output('combat-result', 'children')],
    [Input('pokemon1', 'value'),
     Input('pokemon2', 'value')]
)
def update_combat(pokemon1_id, pokemon2_id):
    # Si aucun Pokémon n'est sélectionné, afficher des valeurs par défaut
    if pokemon1_id is None or pokemon2_id is None:
        return (
            '', '', '', '', '', '', '', '',  # Pokémon 1 vide
            '', '', '', '', '', '', '', '',  # Pokémon 2 vide
            go.Figure(),  # Graphique vide
            ""  # Résultat vide
        )
    
    # Récupérer les Pokémon sélectionnés
    pokemon1 = df_ancienne[df_ancienne['pokemon_id'] == pokemon1_id].iloc[0]
    pokemon2 = df_nouvelle[df_nouvelle['pokemon_id'] == pokemon2_id].iloc[0]
    
    # Mettre à jour les images et les stats
    pokemon1_image = f"/data/Images/{os.path.basename(pokemon1['image_path'])}"
    pokemon2_image = f"/data/Images/{os.path.basename(pokemon2['image_path'])}"
    
    # Créer le graphique en radar
    radar_chart = create_radar_chart(pokemon1, pokemon2)
    
    # Déterminer le gagnant
    result = determine_winner(pokemon1, pokemon2)
    
    return (
        pokemon1_image, pokemon1['name'], f"Génération: {pokemon1['generation']}",
        f"HP: {pokemon1['hp']}", f"Attaque: {pokemon1['attack']}", f"Défense: {pokemon1['defense']}",
        f"Attaque Spéciale: {pokemon1['special_attack']}", f"Défense Spéciale: {pokemon1['special_defense']}",
        f"Vitesse: {pokemon1['speed']}",
        pokemon2_image, pokemon2['name'], f"Génération: {pokemon2['generation']}",
        f"HP: {pokemon2['hp']}", f"Attaque: {pokemon2['attack']}", f"Défense: {pokemon2['defense']}",
        f"Attaque Spéciale: {pokemon2['special_attack']}", f"Défense Spéciale: {pokemon2['special_defense']}",
        f"Vitesse: {pokemon2['speed']}",
        radar_chart, result
    )

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)