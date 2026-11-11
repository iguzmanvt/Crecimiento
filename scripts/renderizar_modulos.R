# Genera notas y presentaciones sin sobrescribir los HTML históricos.
args <- commandArgs(trailingOnly = TRUE)
if (!length(args)) stop("Uso: Rscript scripts/renderizar_modulos.R SALIDA [MODULO_O_ID ...]")
script_arg <- grep("^--file=", commandArgs(), value = TRUE)
if (length(script_arg) != 1) stop("Ejecutar mediante Rscript.")
script <- normalizePath(sub("^--file=", "", script_arg), winslash = "/", mustWork = TRUE)
repo <- dirname(dirname(script))
manifest <- read.csv(file.path(repo, "scripts", "modulos.csv"), stringsAsFactors = FALSE,
                     colClasses = "character", fileEncoding = "UTF-8")
modules <- unique(manifest$module)
if (length(args) > 1) {
  selected <- args[-1]
  valid <- c(modules, manifest$id)
  if (any(!selected %in% valid)) stop("Módulo o ID desconocido: ", paste(setdiff(selected, valid), collapse = ", "))
  manifest <- manifest[manifest$module %in% selected | manifest$id %in% selected, , drop = FALSE]
}
canonical <- function(path) if (.Platform$OS.type == "windows") tolower(path) else path
requested <- path.expand(args[1])
dir.create(requested, recursive = TRUE, showWarnings = FALSE)
out <- normalizePath(requested, winslash = "/", mustWork = TRUE)
if (canonical(out) == canonical(repo) || startsWith(canonical(out), paste0(canonical(repo), "/"))) {
  stop("La salida debe estar fuera del repositorio.")
}
if (length(list.files(out, all.files = TRUE, no.. = TRUE))) stop("El directorio de salida debe estar vacío.")
required <- c("rmarkdown", "knitr", "png", "gridExtra", "plotly", "shiny", "jsonlite")
if (any(grepl("Ejemplo Estados Unidos", manifest$source, fixed = TRUE))) required <- c(required, "pwt10")
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) stop("Faltan paquetes: ", paste(missing, collapse = ", "))
results <- list()
for (i in seq_len(nrow(manifest))) {
  row <- manifest[i, ]
  input <- file.path(repo, row$source)
  for (format in strsplit(row$formats, ";", fixed = TRUE)[[1]]) {
    relative <- file.path(row$module, row$id, format)
    destination <- file.path(out, relative)
    dir.create(destination, recursive = TRUE)
    intermediates <- file.path(destination, "intermedios")
    dir.create(intermediates)
    metadata <- rmarkdown::yaml_front_matter(input)
    options <- list(self_contained = FALSE)
    if (!is.null(metadata$output[[format]]$css)) {
      if (!file.copy(file.path(repo, "Clases_Crecimiento_Economico", "curso.css"), destination)) stop("No se pudo copiar el CSS.")
      options$css <- "curso.css"
    }
    if (nzchar(row$recovered)) {
      resources <- file.path(dirname(input), "recuperado")
      if (!file.copy(resources, destination, recursive = TRUE)) stop("No se pudo copiar la recuperación.")
    }
    cat("RENDER", row$module, row$id, format, "\n")
    started <- Sys.time()
    warnings <- character()
    result <- tryCatch(withCallingHandlers({
      rmarkdown::render(input, output_format = format, output_file = "Material.html",
        output_dir = destination, intermediates_dir = intermediates,
        knit_root_dir = dirname(input), output_options = options,
        envir = new.env(parent = globalenv()), clean = TRUE, quiet = TRUE)
    }, warning = function(w) { warnings <<- c(warnings, conditionMessage(w)); invokeRestart("muffleWarning") }),
    error = function(e) e)
    record <- list(module = row$module, id = row$id, source = row$source, format = format,
      output = gsub("\\\\", "/", file.path(relative, "Material.html")),
      status = if (inherits(result, "error")) "failed" else "passed",
      error = if (inherits(result, "error")) conditionMessage(result) else NULL,
      warnings = unique(warnings), seconds = as.numeric(difftime(Sys.time(), started, units = "secs")))
    results[[length(results) + 1]] <- record
    jsonlite::write_json(list(results = results,
      session = list(R = R.version.string, pandoc = as.character(rmarkdown::pandoc_version()),
        packages = setNames(lapply(required, function(p) as.character(packageVersion(p))), required))),
      file.path(out, "resultados.json"), pretty = TRUE, auto_unbox = TRUE, null = "null")
    if (inherits(result, "error")) cat("FAILED", record$error, "\n") else cat("OK", record$output, "\n")
  }
}
if (any(vapply(results, function(r) r$status != "passed", logical(1)))) stop("Hay salidas fallidas; revisar resultados.json.")
cat("Conservar cada carpeta completa. Las referencias externas requieren conexión y comprobación separada.\n")
