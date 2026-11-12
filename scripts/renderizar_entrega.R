# Renderiza únicamente los 33 materiales canónicos en una carpeta separada.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("Uso: Rscript scripts/renderizar_entrega.R SALIDA [MODULO ...]")
script <- normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)), winslash = "/")
repo <- dirname(dirname(script))
if (!requireNamespace("jsonlite", quietly = TRUE) || !requireNamespace("rmarkdown", quietly = TRUE)) {
  stop("Se requieren jsonlite y rmarkdown, además de los paquetes de las fuentes del curso.")
}
catalog <- jsonlite::fromJSON(file.path(repo, "materiales_actualizados", "catalogo.json"))$materials
if (length(args) > 1) {
  if (any(!args[-1] %in% catalog$module)) stop("Módulo desconocido")
  catalog <- catalog[catalog$module %in% args[-1], , drop = FALSE]
}
dir.create(args[1], recursive = TRUE, showWarnings = FALSE)
out <- normalizePath(args[1], winslash = "/", mustWork = TRUE)
canonical <- function(p) if (.Platform$OS.type == "windows") tolower(p) else p
if (canonical(out) == canonical(repo) || startsWith(canonical(out), paste0(canonical(repo), "/"))) stop("La salida debe quedar fuera del repositorio")
if (length(list.files(out, all.files = TRUE, no.. = TRUE))) stop("La salida debe estar vacía")
records <- list()
for (i in seq_len(nrow(catalog))) {
  row <- catalog[i, ]
  input <- file.path(repo, row$source)
  destination <- file.path(out, "materiales_actualizados", row$module, row$kind)
  dir.create(file.path(destination, "intermedios"), recursive = TRUE)
  metadata <- rmarkdown::yaml_front_matter(input)
  options <- list(self_contained = FALSE)
  css <- metadata$output[[row$format]]$css
  if (!is.null(css)) {
    css_source <- file.path(dirname(input), css)
    if (!file.exists(css_source)) css_source <- file.path(repo, "Clases_Crecimiento_Economico", css)
    if (!file.exists(css_source)) stop("CSS ausente: ", css_source)
    file.copy(css_source, destination, overwrite = TRUE)
    options$css <- basename(css_source)
  }
  recovered <- file.path(dirname(input), "recuperado")
  if (dir.exists(recovered)) file.copy(recovered, destination, recursive = TRUE)
  started <- Sys.time()
  warnings <- character()
  cat("RENDER", row$module, row$kind, "\n")
  result <- tryCatch(withCallingHandlers({
    rmarkdown::render(input, output_format = row$format, output_file = "Material.html",
      output_dir = destination, intermediates_dir = file.path(destination, "intermedios"),
      knit_root_dir = dirname(input), output_options = options,
      envir = new.env(parent = globalenv()), clean = TRUE, quiet = TRUE)
  }, warning = function(w) { warnings <<- c(warnings, conditionMessage(w)); invokeRestart("muffleWarning") }), error = function(e) e)
  records[[length(records) + 1]] <- list(module = row$module, kind = row$kind, source = row$source,
    format = row$format, html = row$html, status = if (inherits(result, "error")) "failed" else "passed",
    error = if (inherits(result, "error")) conditionMessage(result) else NULL,
    warnings = unique(warnings), seconds = as.numeric(difftime(Sys.time(), started, units = "secs")))
  jsonlite::write_json(list(results = records, R = R.version.string,
    pandoc = as.character(rmarkdown::pandoc_version())), file.path(out, "renderizado.json"),
    pretty = TRUE, auto_unbox = TRUE, null = "null")
  if (inherits(result, "error")) cat("FAILED", conditionMessage(result), "\n") else cat("OK", row$html, "\n")
}
if (any(vapply(records, function(x) x$status != "passed", logical(1)))) stop("Hay materiales fallidos")
