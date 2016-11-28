from __future__ import print_function
from keras.models import Sequential
from keras.layers import Activation, TimeDistributed, Dense, RepeatVector, recurrent
from keras.layers.recurrent import LSTM
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import text_to_word_sequence
import numpy as np

def load_data(filename):
    f = open(filename, 'r')
    data = f.read()
    f.close()
    sentences = [text_to_word_sequence(sentence) for sentence in data.split('\n')[:10]]
    vocab = list(set(np.hstack(sentences)))
    
    word_to_ix = {word:ix for ix, word in enumerate(vocab)}
    ix_to_word = {ix:word for ix, word in enumerate(vocab)}
    for i, sentence in enumerate(sentences):
        for j, word in enumerate(sentence):
            sentences[i][j] = word_to_ix[word]
    return (sentences, len(vocab), word_to_ix, ix_to_word)

def process_data(word_sentences, max_len, word_to_ix):
    sequences = np.zeros((len(word_sentences), max_len, len(word_to_ix)))
    for sentence in word_sentences:
        for i, word in enumerate(sentence):
            sequences[:, i, word] = 1.
    return sequences

def create_model(X_vocab_len, X_max_len, y_vocab_len, y_max_len, hidden_size, num_layers):
    model = Sequential()
    model.add(LSTM(hidden_size, input_shape=(X_max_len, X_vocab_len)))
    model.add(RepeatVector(y_max_len))
    for _ in range(num_layers):
        model.add(LSTM(hidden_size, return_sequences=True))
    model.add(TimeDistributed(Dense(y_vocab_len)))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy',
            optimizer='rmsprop',
            metrics=['accuracy'])
    return model

if __name__ == '__main__':
    X, X_vocab_len, X_word_to_ix, X_ix_to_word = load_data('europarl-v8.fi-en.en')
    y, y_vocab_len, y_word_to_ix, y_ix_to_word = load_data('europarl-v8.fi-en.fi')

    X_max_len = max([len(sentence) for sentence in X])
    padded_X = pad_sequences(X, maxlen=X_max_len, dtype='uint8')

    y_max_len = max([len(sentence) for sentence in y])
    padded_y = pad_sequences(y, maxlen=y_max_len, dtype='uint8')
    
    X_sequences = process_data(padded_X, X_max_len, X_word_to_ix)
    print(X_sequences.shape)

    y_sequences = process_data(padded_y, y_max_len, y_word_to_ix)
    print(y_sequences.shape)

    model = create_model(X_vocab_len, X_max_len, y_vocab_len, y_max_len, 100, 3)
    model.fit(X_sequences, y_sequences, batch_size=10, nb_epoch=100, validation_split=0.2, verbose=1)
    print('Done')