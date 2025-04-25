library(dplyr)
library(openxlsx)

Log <- read.csv("C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZ_FINAL_2021.csv", sep="," ,stringsAsFactors = FALSE)
donnees = read.csv("C:/Users/gevab/SAE OUTIL DEV/data_age_graph.csv", sep=";" , stringsAsFactors = FALSE)

donnees$code_insee <- as.character(donnees$code_insee)
donnees$code_insee <- ifelse(
  nchar(donnees$code_insee) == 4,
  paste0("0", donnees$code_insee),
  donnees$code_insee
  )

Log_bis <- Log %>%
  select(COMMUNE, CATL, NBPI, 
          REGION, SURF, TYPL)

# Puis filtrer 
Log_bis <- Log_bis[Log_bis$COMMUNE %in% donnees$code_insee, ]

# Export
write.csv(Log_bis, "C:/Users/gevab/SAE OUTIL DEV/Log.csv", row.names = FALSE, fileEncoding = "UTF-8")
# write.csv(catl_filtre, "C:/Users/gevab/SAE OUTIL DEV/df_CATL.csv", row.names = FALSE, fileEncoding = "UTF-8")
# write.csv(nbpi_filtre, "C:/Users/gevab/SAE OUTIL DEV/df_NBPI.csv", row.names = FALSE, fileEncoding = "UTF-8")
# write.csv(typl_filtre, "C:/Users/gevab/SAE OUTIL DEV/df_TYPL.csv", row.names = FALSE, fileEncoding = "UTF-8")
