
# Category-theoretic framing (notes)

We model spheres as objects in a category `Pop` where morphisms are typed rule-chains.

- Objects: spheres (typed)
- Morphisms: well-typed rule chains R: sigma -> sigma'
- Composition: sequential concatenation of rule-chains
- Identity: empty chain

Monoidal structure:
- Tensor product ⊗ corresponds to parallel composition of independent spheres (disjoint modality sets).
- Unit object: empty sphere with no modalities.

Important properties to formalize:
- Associativity of composition (syntactic)
- Equivariance: group actions on spheres commute with morphisms when rules are equivariant.
