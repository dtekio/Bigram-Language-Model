from flask import Flask, jsonify, send_file
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import io

dirname = os.path.dirname(__file__)
app = Flask(__name__)


def get_all_bigrams(word):
    bigrams_in_word = [word[i:i + 2] for i in range(len(word) - 1)]
    return bigrams_in_word


def data_load():

    with open(os.path.join(dirname, 'names.txt'), 'r') as f:
        names = ['^' + name + '$' for name in f.read().split()]

    list_of_all_bigrams = [bigram for name in names for bigram in
                   get_all_bigrams(name)]


    # Count the frequency of each bigram
    bigram_counts = {}
    for bigram in list_of_all_bigrams:
        if bigram not in bigram_counts:
            bigram_counts[bigram] = 0
        bigram_counts[bigram] += 1

    # Calculate the probability of each bigram
    total_bigrams = sum(bigram_counts.values())

    for bigram in bigram_counts:
        bigram_counts[bigram] /= total_bigrams

    return (bigram_counts, list_of_all_bigrams)


(bigram_counts, list_of_all_bigrams) = data_load()


# Function for generating a new name
@app.route('/')
def generate_name():
    name = ''

    first_letter = random.choice([start for start in list_of_all_bigrams
                                 if start.startswith('^')])[1]
    name += first_letter


    # Continue to generate the name until the last letter in the name
    while name[-1] != '$':

        # Get a list of all bigrams that begin with the last letter in the name
        possible_bigrams = [bigram for bigram in bigram_counts.keys()
                            if bigram[0] == name[-1]]

        # Choose the next letter based on bigram probabilities
        next_letter = random.choices([bigram[1] for bigram in
                possible_bigrams], [bigram_counts[bigram] for bigram in
                possible_bigrams])[0]
        name += next_letter

    # Remove the last character and return the name in title case
    return jsonify(generated_name=name[:-1].title())


# Function to get a table of bigram probabilities in the form of a picture
@app.route('/bigram_table')
def bigram_table():

    # Creating a list of letters from A to Z
    letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]

    # Creating a probability matrix for all possible bigrams
    probabilities_matrix = np.zeros((26, 26))
    for i in range(26):
        for j in range(26):
            bigram = letters[i] + letters[j]

            probability = bigram_counts.get(bigram, 0)

            # Filling in the corresponding cell of the probability matrix
            probabilities_matrix[i, j] = probability

    # Creating a heat map
    (fig, ax) = plt.subplots()
    im = ax.imshow(probabilities_matrix * 100, cmap='magma')

    # Adding the names of the letters on the x and y axis
    ax.set_xticks(np.arange(len(letters)))
    ax.set_yticks(np.arange(len(letters)))
    ax.set_xticklabels(letters)
    ax.set_yticklabels(letters)

    # Rotate the letter names on the x axis
    plt.setp(ax.get_xticklabels(), ha='right', rotation_mode='anchor')

    # Adding a color scale
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Probability, %', rotation=-90, va='bottom')

    # Add a header and show the graph
    ax.set_title('Heat map of bigram probabilities')
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run()