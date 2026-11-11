args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==3)
root <- args[1]; historical_path <- args[2]; repo <- args[3]
e <- new.env(parent=baseenv());utils::data('pwt10.0',package='pwt10',envir=e);installed <- e$pwt10.0
cenv <- new.env(parent=baseenv());invisible(load(file.path(root,'cran_pwt100.rda'),envir=cenv));stopifnot(is.data.frame(cenv$pwt10.0))
calculate <- function(pwt10.0) {
 p <- pwt10.0
 p$lngdppc <- round(log(p$rgdpna) - log(p$pop),digits=2)
 p$ky <- round(p$rnna/p$rgdpna,digits=2)
 p$acctky <- (.3/(1-.3))*log(p$ky)
 p$accthc <- log(p$hc)
 p$accttfp <- p$lngdppc - p$acctky - p$accthc
 p <- p[which(p$year>1959),]
 p$inittfp <- with(p, accttfp[year == '1960'][match(isocode, isocode[year == '1960'])])
 p$inithc <- with(p, accthc[year == '1960'][match(isocode, isocode[year == '1960'])])
 p$initky <- with(p, acctky[year == '1960'][match(isocode, isocode[year == '1960'])])
 p$kyonly <- round(p$inittfp + p$inithc + p$acctky,digits=2)
 p$hconly <- round(p$inittfp + p$accthc + p$initky,digits=2)
 p$tfponly <- round(p$accttfp + p$inithc + p$initky,digits=2)
 p$input <- round(p$inittfp + p$accthc + p$acctky,digits=2)
 usa <- p[which(p$isocode %in% c('USA')),]
}
source_path <- file.path(repo,'Clases_Crecimiento_Economico','Accounting','Ejemplo Estados Unidos.Rmd')
source_lines <- readLines(source_path,encoding='UTF-8',warn=FALSE)
start <- grep('^```\\{r calculos',source_lines);stopifnot(length(start)==1)
end <- start + which(source_lines[(start+1):length(source_lines)]=='```')[1]
expressions <- as.list(parse(text=source_lines[(start+1):(end-1)],keep.source=FALSE))
canonical <- function(x) paste(deparse(x,width.cutoff=500L),collapse='\n')
formula_exact <- identical(vapply(expressions,canonical,''),vapply(as.list(body(calculate))[-1],canonical,''));stopifnot(formula_exact)
inputs <- jsonlite::fromJSON(file.path(root,'USA_inputs_for_R.json'))
frames <- lapply(inputs,function(d) {d <- d[,c('isocode','year','rgdpna','rnna','pop','hc')];for(k in c('year','rgdpna','rnna','pop','hc'))d[[k]]<-as.numeric(d[[k]]);d})
frames$cran_download <- cenv$pwt10.0
traces <- lapply(frames,calculate);ref <- calculate(installed)
years <- as.integer(ref$year);stopifnot(identical(years,1960:2019))
trace_names <- c('kyonly','hconly','tfponly','lngdppc');derived <- c('ky','acctky','accthc','accttfp','inittfp','inithc','initky',trace_names,'input')
comparisons <- lapply(names(traces),function(n) {
 d<-traces[[n]];stopifnot(identical(as.integer(d$year),years));list(source=n,rows=nrow(d),ky_rounded_exact=identical(as.numeric(d$ky),as.numeric(ref$ky)),all_derived_numeric_exact=all(vapply(derived,function(k)identical(as.numeric(d[[k]]),as.numeric(ref[[k]])),logical(1))),traces=lapply(trace_names,function(k)list(variable=k,values=length(d[[k]]),mismatches=sum(d[[k]]!=ref[[k]]),max_abs_difference=max(abs(d[[k]]-ref[[k]])),differing_years=years[d[[k]]!=ref[[k]]])))
})
henv<-new.env(parent=baseenv());invisible(load(historical_path,envir=henv));hp<-get('pwt10.0',envir=henv,inherits=FALSE);hu<-get('usa',envir=henv,inherits=FALSE);stopifnot(is.data.frame(hp),is.data.frame(hu));hu<-hu[order(hu$year),]
historical<-list(context='Workspace localizado en carpeta de curso Otoño 2021; no fecha de creación autenticada sólo por nombre de carpeta',file_bytes=unname(file.info(historical_path)$size),file_md5=unname(tools::md5sum(historical_path)),pwt_rows=nrow(hp),pwt_columns=ncol(hp),pwt_identical_to_installed=identical(hp,installed),usa_rows=nrow(hu),usa_columns=ncol(hu),USA_years=range(hu$year),year_sequence_equal=identical(as.integer(hu$year),years),required_inputs_exact=all(vapply(c('year','rgdpna','rnna','pop','hc'),function(k)identical(as.numeric(hu[[k]]),as.numeric(ref[[k]])),logical(1))),all_derived_numeric_exact=all(vapply(derived,function(k)identical(as.numeric(hu[[k]]),as.numeric(ref[[k]])),logical(1))),traces=lapply(trace_names,function(k)list(variable=k,mismatches=sum(hu[[k]]!=ref[[k]]),max_abs_difference=max(abs(hu[[k]]-ref[[k]])))))
result<-list(R=R.version.string,DESCRIPTION_version=utils::packageDescription('pwt10')$Version,object='pwt10.0',downloaded_CRAN_object_identical_to_installed=identical(installed,cenv$pwt10.0),calculation_expressions_exact_to_published_Rmd=formula_exact,baseline='d8613e6a2fe63c1b7b3659ab3211895686c14dce',period=c(1960,2019),comparisons=comparisons,historical_workspace=historical,Rmd_document_executed=FALSE,api_create_executed=FALSE,workbook_recalculated=FALSE)
jsonlite::write_json(result,file.path(root,'trace_effect_audit.json'),auto_unbox=TRUE,pretty=TRUE,na='null')
output<-data.frame(year=years)
for(n in names(traces)) for(k in trace_names) output[[paste(n,k,sep='_')]]<-traces[[n]][[k]]
for(k in trace_names)output[[paste('historical_usa',k,sep='_')]]<-hu[[k]]
write.csv(output,file.path(root,'USA_trace_comparison_1960_2019.csv'),row.names=FALSE,fileEncoding='UTF-8')
cat(jsonlite::toJSON(result,auto_unbox=TRUE,pretty=TRUE,na='null'))
