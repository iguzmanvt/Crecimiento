# Repite el contraste USA con entradas archivadas y las fórmulas del Rmd.
script_arg <- grep("^--file=", commandArgs(), value = TRUE)
stopifnot(length(script_arg) == 1)
script <- normalizePath(sub("^--file=", "", script_arg), winslash = "/", mustWork = TRUE)
repo <- dirname(dirname(script))
input_path <- file.path(repo, "verificacion", "pendientes_20261111", "pwt", "USA_inputs_for_R.json")
source_path <- file.path(repo, "Clases_Crecimiento_Economico", "Accounting", "Ejemplo Estados Unidos.Rmd")
lines <- readLines(source_path, encoding = "UTF-8", warn = FALSE)
start <- grep("^```\\{r calculos", lines)
stopifnot(length(start) == 1)
end <- start + which(lines[(start + 1):length(lines)] == "```")[1]
code <- parse(text = lines[(start + 1):(end - 1)])
inputs <- jsonlite::fromJSON(input_path)
inputs <- lapply(inputs, function(d) {
  stopifnot(is.data.frame(d), all(c("isocode", "year", "rgdpna", "rnna", "pop", "hc") %in% names(d)))
  for (v in c("year", "rgdpna", "rnna", "pop", "hc")) {
    d[[v]] <- as.numeric(d[[v]])
    stopifnot(all(is.finite(d[[v]])), all(d[[v]] > 0))
  }
  d
})
package_env <- new.env(parent = baseenv())
utils::data("pwt10.0", package = "pwt10", envir = package_env)
calculate <- function(data) {
  env <- new.env(parent = baseenv())
  env$pwt10.0 <- data
  eval(code, envir = env)
  env$usa[order(env$usa$year), ]
}
reference <- calculate(package_env$pwt10.0)
stopifnot(identical(as.integer(reference$year), 1960:2019))
variables <- c("ky", "acctky", "accthc", "accttfp", "inittfp", "inithc", "initky",
               "kyonly", "hconly", "tfponly", "lngdppc", "input")
results <- lapply(names(inputs), function(name) {
  actual <- calculate(inputs[[name]])
  stopifnot(identical(as.integer(actual$year), 1960:2019))
  same <- vapply(variables, function(v) identical(as.numeric(actual[[v]]), as.numeric(reference[[v]])), logical(1))
  stopifnot(all(same))
  list(source = name, years = 60, traces = 4, trace_values_equal = 240,
       derived_values_equal = 720, mismatches = 0)
})
original <- inputs$repo_excel
package_usa <- package_env$pwt10.0[package_env$pwt10.0$isocode == "USA", ]
package_usa <- package_usa[match(original$year, package_usa$year), ]
stopifnot(sum(original$rnna != package_usa$rnna) == 35)
cat(jsonlite::toJSON(list(object = "pwt10.0", package_DESCRIPTION_version = utils::packageDescription("pwt10")$Version,
  rnna_input_differences = 35, results = results,
  scope = "Entradas archivadas; no vuelve a descargar las tablas oficiales ni valida otros cálculos."),
  auto_unbox = TRUE, pretty = TRUE), "\n")
