# latexmkrc for RSVP monograph
$pdf_mode = 1;
$clean_ext = "bbl run.xml";
$biber = "biber %O %B";

add_cus_dep( 'bib', 'bbl', 0, 'run_biber' );

sub run_biber {
    system( "biber @_ " );
}

$latex = 'lualatex --shell-escape %O %S';
$bibtex_use = 2;

push @default_files, 'monograph.tex';

