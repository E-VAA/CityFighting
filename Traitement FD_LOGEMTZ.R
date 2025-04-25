library(dplyr)
library(openxlsx)
install.packages("insee")
library(insee)


# Log_A <- read.csv("C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZA_2021.csv", sep=";" ,stringsAsFactors = FALSE)
# Log_B <- read.csv("C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZB_2021.csv", sep=";" ,stringsAsFactors = FALSE)
# Log_C <- read.csv("C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZC_2021.csv", sep=";" , stringsAsFactors = FALSE)
# Log_D <- read.csv("C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZD_2021.csv", sep=";" , stringsAsFactors = FALSE)
# Log_E <- read.csv("C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZE_2021.csv", sep=";" , stringsAsFactors = FALSE)
# 
# # Nettoyage
# Log_A_bis <- Log_A %>%
#   select(COMMUNE, ARM, CATL, NBPI, STOCD, HLML, IRANM, 
#          METRODOM, REGION, SURF, TYPC, TYPL, TRIRIS)
# Log_B_bis <- Log_B %>%
#   select(COMMUNE, ARM, CATL, NBPI, STOCD, HLML, IRANM, 
#          METRODOM, REGION, SURF, TYPC, TYPL, TRIRIS)
# Log_C_bis <- Log_C %>%
#   select(COMMUNE, ARM, CATL, NBPI, STOCD, HLML, IRANM, 
#          METRODOM, REGION, SURF, TYPC, TYPL, TRIRIS)
# Log_D_bis <- Log_D %>%
#   select(COMMUNE, ARM, CATL, NBPI, STOCD, HLML, IRANM, 
#          METRODOM, REGION, SURF, TYPC, TYPL, TRIRIS)
# Log_E_bis <- Log_E %>%
#   select(COMMUNE, ARM, CATL, NBPI, STOCD, HLML, IRANM, 
#          METRODOM, REGION, SURF, TYPC, TYPL, TRIRIS)
# 
# # Traitement (Commune avec 0 devant les chaines de 4)
# # Pas nécessaire pour Log_A_bis
# Log_B_bis$COMMUNE <- ifelse(
#   nchar(Log_B_bis$COMMUNE) == 4,
#   paste0("0", Log_B_bis$COMMUNE),
#   Log_B_bis$COMMUNE
# )
# Log_C_bis$COMMUNE <- ifelse(
#   nchar(Log_C_bis$COMMUNE) == 4,
#   paste0("0", Log_C_bis$COMMUNE),
#   Log_C_bis$COMMUNE
# )
# Log_D_bis$COMMUNE <- ifelse(
#   nchar(Log_D_bis$COMMUNE) == 4,
#   paste0("0", Log_D_bis$COMMUNE),
#   Log_D_bis$COMMUNE
# )
# Log_E_bis$COMMUNE <- ifelse(
#   nchar(Log_E_bis$COMMUNE) == 4,
#   paste0("0", Log_E_bis$COMMUNE),
#   Log_E_bis$COMMUNE
# )
# 
# #Regroupement 
# Log<- rbind(Log_A_bis, Log_B_bis, Log_C_bis, Log_D_bis, Log_E_bis)

# # Export
#write.csv(Log, "C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZ_FINAL_2021.csv", row.names = FALSE, fileEncoding = "UTF-8")
ville = read.csv("C:/Users/gevab/SAE OUTIL DEV/donnees_pop.csv", sep=';')
Log <- read.csv("C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZ_FINAL_2021.csv", sep="," ,stringsAsFactors = FALSE)
# Log_bis <- Log %>%
#    select(COMMUNE, CATL, NBPI, STOCD, 
#           REGION, SURF, TYPL, TRIRIS)
Log <- merge(Log, ville, by.x = "COMMUNE", by.y = "CODGEO", all.x = TRUE)

Log_bis <- Log %>%
   select(COMMUNE, LIBGEO, CATL, NBPI, STOCD, 
          REGION, SURF, TYPL, TRIRIS)

write.csv(Log_bis, "C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZ_FINAL_2021.csv", row.names = FALSE, fileEncoding = "UTF-8")
