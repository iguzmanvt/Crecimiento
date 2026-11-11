"""Comprueba rutas literales de readPNG/readJPEG sin ejecutar las fuentes Rmd."""
import argparse
import csv
import json
from pathlib import Path
import posixpath
import re
import subprocess
import tempfile

IMAGE_CALL = re.compile(r'''\b(?P<reader>readPNG|readJPEG)\s*\(\s*(?P<quote>["'])(?P<path>[^"']+)(?P=quote)''')

R_CHECK = r'''
args <- commandArgs(trailingOnly=TRUE)
input <- read.csv(args[1], stringsAsFactors=FALSE, fileEncoding="UTF-8")
for (pkg in c("png", "jpeg")) {
  if (!requireNamespace(pkg, quietly=TRUE)) stop(paste("Falta el paquete", pkg))
}
output <- input[c("relative_path", "reader")]
output$height <- integer(nrow(input))
output$width <- integer(nrow(input))
output$warning <- character(nrow(input))
for (i in seq_len(nrow(input))) {
  notes <- character()
  img <- withCallingHandlers(
    if (input$reader[i] == "readPNG") png::readPNG(input$path[i], native=TRUE)
    else jpeg::readJPEG(input$path[i], native=TRUE),
    warning=function(w) { notes <<- c(notes, conditionMessage(w)); invokeRestart("muffleWarning") }
  )
  shape <- dim(img)
  if (length(shape) < 2 || any(shape[1:2] <= 0)) stop("Imagen sin dimensiones validas")
  output$height[i] <- shape[1]
  output$width[i] <- shape[2]
  output$warning[i] <- paste(notes, collapse=" | ")
  rm(img)
}
write.csv(output, args[2], row.names=FALSE, fileEncoding="UTF-8")
cat(R.version.string, "\n")
cat("png", as.character(packageVersion("png")), "jpeg", as.character(packageVersion("jpeg")), "\n")
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rscript', default='Rscript', help='Ejecutable Rscript disponible en el equipo')
    parser.add_argument('--report', type=Path, help='Informe JSON opcional, preferiblemente fuera del repositorio')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    tracked = set(subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z']).decode('utf-8').split('\0')) - {''}
    documents = sorted(p for p in tracked if p.endswith('.Rmd'))
    references, issues = [], []
    for document in documents:
        source = (root / document).read_text(encoding='utf-8')
        for match in IMAGE_CALL.finditer(source):
            literal = match['path']
            line = source.count('\n', 0, match.start()) + 1
            if re.match(r'^(?:[A-Za-z]:[/\\]|/|\\\\)', literal) or '\\' in literal:
                issues.append(f'{document}:{line}: ruta absoluta o separador no portable')
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(document), literal))
            if target not in tracked or not (root / target).is_file():
                issues.append(f'{document}:{line}: recurso ausente o nombre no exacto: {literal}')
                continue
            expected_extension = '.png' if match['reader'] == 'readPNG' else '.jpg'
            if not target.lower().endswith(expected_extension):
                issues.append(f'{document}:{line}: formato no esperado para {match["reader"]}')
                continue
            references.append({'rmd': document, 'line': line, 'reader': match['reader'], 'literal': literal, 'target': target})
    if issues:
        raise SystemExit('\n'.join(issues))
    if not references:
        raise SystemExit('No se encontraron lecturas literales de imagen para comprobar.')
    unique = sorted({(r['target'], r['reader']) for r in references})
    with tempfile.TemporaryDirectory(prefix='crecimiento-images-') as temp:
        temp = Path(temp)
        manifest, result, script = temp / 'images.csv', temp / 'decoded.csv', temp / 'decode.R'
        with manifest.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['relative_path', 'reader', 'path'])
            writer.writerows((name, reader, str(root / name)) for name, reader in unique)
        script.write_text(R_CHECK, encoding='utf-8')
        run = subprocess.run([args.rscript, '--vanilla', str(script), str(manifest), str(result)], text=True, encoding='utf-8', errors='replace', capture_output=True)
        if run.returncode:
            raise SystemExit(run.stdout + run.stderr)
        with result.open(encoding='utf-8-sig', newline='') as handle:
            decoded = list(csv.DictReader(handle))
        if len(decoded) != len(unique):
            raise SystemExit('La lectura de imagenes no cubrio todos los archivos.')
    summary = {
        'rmd_scanned': len(documents),
        'rmd_with_image_calls': len({r['rmd'] for r in references}),
        'references_verified': len(references),
        'unique_images_decoded': len(decoded),
        'png_files': sum(r['reader'] == 'readPNG' for r in decoded),
        'jpeg_files': sum(r['reader'] == 'readJPEG' for r in decoded),
        'image_warnings': sum(bool(r['warning']) for r in decoded),
        'r_environment': run.stdout.strip().splitlines(),
        'scope': 'Rutas literales y decodificacion de imagenes; no ejecuta Rmd ni valida fuentes estadisticas, estilos o enlaces externos.',
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps({'summary': summary, 'references': references, 'images': decoded}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
