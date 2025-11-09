-- Lean 4 draft: Sphere signatures and simple rule type
-- This is a lightweight formalization sketch for SpherePOP types.

structure Sphere where
  id : String
  types : List String
  -- modalities omitted for brevity

inductive Modality where
  | text
  | audio
  deriving Repr

structure Rule where
  name : String
  input : Modality
  output : Modality
  budget : Float

def ttsRule : Rule := { name := "tts", input := Modality.text, output := Modality.audio, budget := 0.05 }

#eval ttsRule.name
