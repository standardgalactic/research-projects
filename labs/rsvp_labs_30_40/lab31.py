# lab31.py stub

def init(params):
    return {'t':0}

def step(state, params, dt):
    state['t']+=dt
    return state

def frame(state):
    return state
