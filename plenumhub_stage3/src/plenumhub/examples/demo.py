from plenumhub import Sphere, Rule, Interpreter

def run_demo():
    it = Interpreter()
    s = Sphere(id='s0', T=['text'], M={'text':'Entropy bounds matter.'}, E=0.1)
    it.add_sphere(s)
    r = Rule(name='tts', in_mod='text', out_mod='audio', epsilon=0.02)
    it.register_rule(r)
    out = it.pop('s0', 's1', ['tts'])
    print('Produced sphere:', out)
    merged = it.merge('s0','s1','s2')
    print('Merged sphere id:', merged.id, 'E=', merged.E)

if __name__ == '__main__':
    run_demo()
