import os

STATE_FILE = 'key_state.txt'

def _read_indices():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            lines = f.readlines()
        while len(lines) < 2:
            lines.append('0\n')
        return [int(line.strip()) for line in lines]
    else:
        return [0, 0]

def _write_indices(indices):
    with open(STATE_FILE, 'w') as f:
        for index in indices:
            f.write(f"{index}\n")

def get_elevenlabs_key():
    # List of ElevenLabs Keys
    keys = ['sk_keyAsString']
    
    indices = _read_indices()
    index = indices[0]
    item = keys[index % len(keys)]
    indices[0] = (index + 1) % len(keys)
    _write_indices(indices)
    return item

def get_groq_key():
    # List of Groq Keys
    keys = ['gsk_keyAsString']
    
    indices = _read_indices()
    index = indices[1]
    item = keys[index % len(keys)]
    indices[1] = (index + 1) % len(keys)
    _write_indices(indices)
    return item
