import os
from flask import Flask, render_template, request
import requests
import random
from datetime import datetime

app = Flask(__name__)

base_url = "https://pokeapi.co/api/v2/"

def Pokeverse(pokemon_name):
    url = f'{base_url}pokemon/{pokemon_name}'
    try:
        response = requests.get(url)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokémon info for {pokemon_name}: {e}")
        return None

def get_pokemon_type(pokemon_name):
    url = f"{base_url}pokemon/{pokemon_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        pokemon_data = response.json()
        primary_type = pokemon_data['types'][0]['type']['name']
        return primary_type
    except (requests.exceptions.RequestException, IndexError) as e:
        print(f"Error fetching Pokémon type for {pokemon_name}: {e}")
        return 'main' 

def get_pokemon_of_day():
    """Get a random Pokémon for the current day using a seeded random generator"""
    try:
        response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=10000')
        response.raise_for_status()
        data = response.json()
        pokemon_list = [pokemon['name'] for pokemon in data['results']]
        
        if not pokemon_list:
            return None
            
        today = datetime.now()
        day_of_year = today.timetuple().tm_yday
        year = today.year
        
        daily_seed = year * 1000 + day_of_year
        random.seed(daily_seed)
        random_pokemon = random.choice(pokemon_list)
        random.seed()
        
        return random_pokemon
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokémon list for daily Pokémon: {e}")
        return None
    except Exception as e:
        print(f"Error in get_pokemon_of_day: {e}")
        return None


@app.route('/')
@app.route('/home')
def home():
    pokemon_list = []
    pokemon_of_day = None
    
    try:
        response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=10000')
        response.raise_for_status()
        data = response.json()
        pokemon_list = [pokemon['name'] for pokemon in data['results']]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all Pokémon names for home page: {e}")
        pokemon_list = []
    except KeyError:
        print("API response for all Pokémon names did not contain 'results' key.")
        pokemon_list = []
    
    pokemon_of_day_name = get_pokemon_of_day()
    if pokemon_of_day_name:
        try:
            pokemon_of_day = Pokeverse(pokemon_of_day_name)
        except Exception as e:
            print(f"Error fetching Pokémon of the Day data: {e}")
            pokemon_of_day = None
    
    return render_template('home.html', 
                         pokemon_list=pokemon_list, 
                         pokemon_of_day=pokemon_of_day)


@app.route('/pokedex', methods=['GET', 'POST'])
def pokedex():
    pokemon_info = None
    primary_type = 'main'
    pokemon_list = [] 
    
    try:
        response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=10000')
        response.raise_for_status()
        data = response.json()
        pokemon_list = [pokemon['name'] for pokemon in data['results']]
        print(f"Successfully loaded {len(pokemon_list)} Pokémon for autocomplete")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all Pokémon names for autocomplete: {e}")
        pokemon_list = [] 
    except KeyError:
        print("API response for all Pokémon names did not contain 'results' key.")
        pokemon_list = [] 
    
    if request.method == 'GET' and request.args.get('pokemon'):
        name = request.args.get('pokemon').lower()
        pokemon_data = Pokeverse(name) 
        if pokemon_data: 
            pokemon_info = pokemon_data
            if pokemon_data['types']: 
                primary_type = pokemon_data['types'][0]['type']['name']
            else:
                primary_type = 'normal' 
    
    elif request.method == 'POST':
        name = request.form['pokemon_name'].lower()
        pokemon_data = Pokeverse(name) 
        if pokemon_data: 
            pokemon_info = pokemon_data
            if pokemon_data['types']: 
                primary_type = pokemon_data['types'][0]['type']['name']
            else:
                primary_type = 'normal' 
        else:
            pass

    return render_template('pokedex.html',
                           pokemon_info=pokemon_info,
                           pokemon_list=pokemon_list, 
                           primary_type=primary_type)

@app.route('/games')
def games():
    return render_template("games.html")

@app.route('/pokemon_guess')
def pokemon_guess():
    return render_template('pokemon_guess.html')

@app.route('/pokemon_quiz')
def pokemon_quiz():
    return render_template('pokemon_quiz.html')
