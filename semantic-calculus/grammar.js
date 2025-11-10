
// grammar.js - tree-sitter grammar scaffold for SpherePOP
// Note: this is a scaffold; refine token patterns and precedence as needed.

module.exports = grammar({
  name: 'spherepop',

  extras: $ => [/\s/, $.comment],

  rules: {
    source_file: $ => repeat($._statement),

    _statement: $ => choice(
      $.let_binding,
      $.sphere_decl,
      $.policy_exec
    ),

    let_binding: $ => seq('let', $.identifier, '=', $._expr),

    sphere_decl: $ => seq('sphere', $.identifier, '=', $.sphere),

    policy_exec: $ => seq('apply', $.policy, 'to', $.identifier),

    _expr: $ => choice(
      $.sphere,
      $.policy,
      seq($._expr, 'merge', $._expr),
      seq($.policy, '(', $._expr, ')')
    ),

    sphere: $ => seq('{',
      'field', ':', $.field_map, ',',
      'boundary', ':', $.boundary, ',',
      'entropy', ':', $.number,
      '}'),

    field_map: $ => seq('{', commaSep($.field_pair), '}'),
    field_pair: $ => seq($.identifier, ':', $.vector),
    vector: $ => seq('[', optional(commaSep1($.number)), ']'),
    boundary: $ => seq('∂', $.identifier),

    policy: $ => choice('pop', 'collapse', seq('rewrite', $.identifier), seq('mask', $.identifier), seq('allocate', $.number)),

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,
    number: $ => /[0-9]+(\.[0-9]+)?/,

    comment: $ => token(seq('//', /.*/))
  }
});

function commaSep (rule) {
  return seq(rule, repeat(seq(',', rule)));
}
function commaSep1 (rule) {
  return seq(rule, repeat(seq(',', rule)));
}
