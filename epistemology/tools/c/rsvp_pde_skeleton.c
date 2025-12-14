nclude <stdio.h>
#include <stdlib.h>

/*
  rsvp-pde-skeleton
  Emits a *symbolic* RSVP-style PDE scaffold (safe / non-operational).
  Usage: rsvp-pde-skeleton > derivations.tex
*/

int main(void) {
  puts("% Auto-generated PDE scaffold (symbolic)");
  puts("\\begin{align}");
  puts("\\partial_t \\Phi &= -\\nabla\\cdot(\\Phi\\,\\mathbf{v}) + D_\\Phi\\,\\Delta\\Phi + \\mathcal{N}_\\Phi(\\Phi,\\mathbf{v},S)\\\\");
  puts("\\partial_t \\mathbf{v} &= - (\\mathbf{v}\\cdot\\nabla)\\mathbf{v} - \\nabla P(\\Phi,S) + \\nu\\,\\Delta\\mathbf{v} + \\mathcal{N}_v(\\Phi,\\mathbf{v},S)\\\\");
  puts("\\partial_t S &= -\\nabla\\cdot(S\\,\\mathbf{v}) + D_S\\,\\Delta S + \\sigma(\\Phi,\\mathbf{v},S)");
  puts("\\end{align}");
  puts("");
  puts("% Notes:");
  puts("% - \\mathcal{N}_\\Phi, \\mathcal{N}_v: nonlinear couplings");
  puts("% - P: effective pressure/constraint potential");
  puts("% - \\sigma: entropy production (nonnegative by construction if desired)");
  return 0;
}

