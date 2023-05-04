from flask import Flask, jsonify, send_file
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import io

dirname = os.path.dirname(__file__)
app = Flask(__name__)

# Function to get all bigrams in a word
def get_bigrams(word):
    return [word[i:i+2] for i in range(len(word)-1)]

def load_data():
    # Read the data from the file and break it down into words
    with open(os.path.join(dirname, 'names.txt'), 'r') as f:
        names = ["^" + name + "$" for name in f.read().split()]

    # List of all bigrams in names
    all_bigrams = [bigram for name in names for bigram in get_bigrams(name)]

    # Count the frequency of each bigram
    bigram_counts = {}
    for bigram in all_bigrams:
        if bigram not in bigram_counts:
            bigram_counts[bigram] = 0
        bigram_counts[bigram] += 1

    # Calculate the probability of each bigram
    total_bigrams = sum(bigram_counts.values())

    for bigram in bigram_counts:
        bigram_counts[bigram] /= total_bigrams

    return bigram_counts, all_bigrams


bigram_counts, all_bigrams = load_data()

# Function to get a table of bigram probabilities in the form of a picture
@app.route("/bigram_table")
def print_bigram_table():
    # Creating a list of letters from A to Z
    letters = [chr(i) for i in range(ord('a'), ord('z')+1)]

    # Creating a probability matrix for all possible bigrams
    probs_matrix = np.zeros((26, 26))
    for i in range(26):
        for j in range(26):
            bigram = letters[i] + letters[j]
            # Get the probability for the current bigram from the dictionary
            prob = bigram_counts.get(bigram, 0)
            # Filling in the corresponding cell of the probability matrix
            probs_matrix[i, j] = prob

    # Creating a heat map
    fig, ax = plt.subplots()
    im = ax.imshow(probs_matrix * 100, cmap='magma')

    # Adding the names of the letters on the x and y axis
    ax.set_xticks(np.arange(len(letters)))
    ax.set_yticks(np.arange(len(letters)))
    ax.set_xticklabels(letters)
    ax.set_yticklabels(letters)

    # Rotate the letter names on the x axis
    plt.setp(ax.get_xticklabels(), ha="right",
            rotation_mode="anchor")

    # Adding a color scale
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Probability, %', rotation=-90, va="bottom")

    # Add a header and show the graph
    ax.set_title("Heat map of bigram probabilities")
    fig.tight_layout()
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

# Function for generating a new name
@app.route("/")
def generate_name():
    name = ""
    # Choose a random first letter out of all the letters in the names
    first_letter = random.choice([start for start in all_bigrams if start.startswith("^")])[1]
    name += first_letter
    
    # Continue to generate the name until we select the last letter in the name
    while name[-1] != '$':
        # Get a list of all bigrams that begin with the last letter in the name
        possible_bigrams = [bigram for bigram in bigram_counts.keys() if bigram[0] == name[-1]]
        # Choose the next letter based on bigram probabilities
        next_letter = random.choices([bigram[1] for bigram in possible_bigrams], [bigram_counts[bigram] for bigram in possible_bigrams])[0]
        name += next_letter
    # Remove the last character and return the name in title case
    return jsonify(generated_name=name[:-1].title())

if __name__ == '__main__':
    app.run(debug=True)