# Genera las dos variantes y ambos formatos fuera del repositorio.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Uso: Rscript scripts/renderizar_introduccion.R DIRECTORIO_SALIDA")
script_arg <- grep("^--file=", commandArgs(), value = TRUE)
if (length(script_arg) != 1) stop("Ejecutar este archivo mediante Rscript.")
script <- normalizePath(sub("^--file=", "", script_arg), winslash = "/", mustWork = TRUE)
repo <- dirname(dirname(script))
requested <- path.expand(args[1])
dir.create(requested, recursive = TRUE, showWarnings = FALSE)
out <- normalizePath(requested, winslash = "/", mustWork = TRUE)
canonical <- function(path) if (.Platform$OS.type == "windows") tolower(path) else path
if (canonical(out) == canonical(repo) || startsWith(canonical(out), paste0(canonical(repo), "/"))) {
  stop("La salida debe estar fuera del repositorio para conservar los materiales históricos.")
}
if (length(list.files(out, all.files = TRUE, no.. = TRUE))) stop("El directorio de salida debe estar vacío.")
if (!requireNamespace("jsonlite", quietly = TRUE)) stop("Se requiere jsonlite.")
# Detecta Pandoc ya instalado con RStudio cuando no está en PATH.
if (!rmarkdown::pandoc_available()) {
  if (.Platform$OS.type == "windows") {
    candidate <- file.path(Sys.getenv("ProgramFiles"), "RStudio", "resources", "app", "bin", "quarto", "bin", "tools", "pandoc.exe")
    if (file.exists(candidate)) {
      Sys.setenv(RSTUDIO_PANDOC = dirname(candidate))
      rmarkdown::find_pandoc(cache = FALSE)
    }
  }
  if (!rmarkdown::pandoc_available()) stop("Se requiere Pandoc; agregar su carpeta a PATH o configurar RSTUDIO_PANDOC.")
}

python <- Sys.which(if (.Platform$OS.type == "windows") "python" else "python3")
if (!nzchar(python)) stop("Se requiere Python 3 para preparar las rutas y fórmulas locales.")
helper <- file.path(repo, "scripts", "postprocesar_render.py")
postprocess <- function(parameters) {
  output <- system2(python, c(shQuote(helper), shQuote(repo), shQuote(out), parameters), stdout = TRUE, stderr = TRUE)
  if (length(output)) cat(paste(output, collapse = "\n"), "\n")
  status <- attr(output, "status")
  if (!is.null(status) && status != 0) stop("Falló la preparación o revisión de recursos locales.")
}
postprocess("--prepare")
intro <- file.path(repo, "Clases_Crecimiento_Economico", "Introduction")
sources <- c("Crecimiento Economico 1.Rmd", "Crecimiento Economico Intro.Rmd")
names <- c("con_tabla", "sin_tabla")
formats <- c("ioslides_presentation", "html_document")
results <- list()
for (i in seq_along(sources)) {
  for (format in formats) {
    destination <- file.path(out, paste(names[i], format, sep = "_"))
    dir.create(destination)
    if (!file.copy(file.path(intro, "introduction.css"), destination)) stop("No se pudo copiar el CSS local.")
    intermediates <- file.path(destination, "intermedios")
    dir.create(intermediates)
    result <- rmarkdown::render(
      file.path(intro, sources[i]), output_format = format,
      output_file = "Introduccion.html", output_dir = destination,
      intermediates_dir = intermediates, knit_root_dir = intro,
      output_options = list(self_contained = FALSE, css = "introduction.css"),
      envir = new.env(parent = globalenv()), clean = TRUE, quiet = TRUE
    )
    postprocess(c("--html", shQuote(result)))
    results[[length(results) + 1]] <- list(variant = names[i], format = format,
      output = gsub("\\\\", "/", file.path(basename(destination), "Introduccion.html")), status = "passed")
    jsonlite::write_json(list(results = results, R = R.version.string,
      pandoc = as.character(rmarkdown::pandoc_version())), file.path(out, "resultados.json"),
      pretty = TRUE, auto_unbox = TRUE, null = "null")
    cat("Generado:", result, "\n")
  }
}
cat("Conservar la carpeta de salida completa, incluidos los recursos compartidos y vendor/mathjax.\n")
