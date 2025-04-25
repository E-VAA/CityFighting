# library(dplyr)
# library(openxlsx)
# install.packages("insee")
# library(insee)


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
# ville = read.csv("C:/Users/gevab/SAE OUTIL DEV/donnees_pop.csv", sep=';')
# Log <- read.csv("C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZ_FINAL_2021.csv", sep="," ,stringsAsFactors = FALSE)
# Log_bis <- Log %>%
#    select(COMMUNE, CATL, NBPI, STOCD, 
#           REGION, SURF, TYPL, TRIRIS)
# Log <- merge(Log, ville, by.x = "COMMUNE", by.y = "CODGEO", all.x = TRUE)
# 
# Log_bis <- Log %>%
#   select(COMMUNE, LIBGEO, CATL, NBPI, STOCD, 
#          REGION, SURF, TYPL, TRIRIS)
# 
# write.csv(Log_bis, "C:/Users/gevab/SAE OUTIL DEV/FD_LOGEMTZ_FINAL_2021.csv", row.names = FALSE, fileEncoding = "UTF-8")



################################
# data <- read.csv("C:/Users/rayan/OneDrive/Documents/sae ouTils/FD_LOGEMTZ_FINAL_2021.csv", sep = ",", header = TRUE)
# View(data)
# head(data)
# data <- subset(data, select = -c(TRIRIS, STOCD,LIBGEO))
# 
# df_CATL <- data[, c("COMMUNE", "REGION", "CATL")]
# df_NBPI <- data[, c("COMMUNE", "REGION", "NBPI")]
# df_SURF <- data[, c("COMMUNE", "REGION", "SURF")]
# df_TYPL <- data[, c("COMMUNE", "REGION", "TYPL")]
# 
# 
# head(df_CATL)
# head(df_NBPI)
# head(df_SURF)
# head(df_TYPL)
# 
# 
# write.csv(df_CATL, "df_CATL.csv", row.names = FALSE)
# write.csv(df_NBPI, "df_NBPI.csv", row.names = FALSE)
# write.csv(df_SURF, "df_SURF.csv", row.names = FALSE)
# write.csv(df_TYPL, "df_TYPL.csv", row.names = FALSE)
# setwd("C:/Users/rayan/OneDrive/Documents/sae ouTils")
# 
# list.files()

################################
library(dplyr)
library(openxlsx)

NBPI <- read.csv("C:/Users/gevab/SAE OUTIL DEV/df_NBPI.csv", sep="," ,stringsAsFactors = FALSE)
CATL <- read.csv("C:/Users/gevab/SAE OUTIL DEV/df_CATL.csv", sep="," ,stringsAsFactors = FALSE)
SURF <- read.csv("C:/Users/gevab/SAE OUTIL DEV/df_SURF.csv", sep="," ,stringsAsFactors = FALSE)
TYPL <- read.csv("C:/Users/gevab/SAE OUTIL DEV/df_TYPL.csv", sep="," ,stringsAsFactors = FALSE)
donnees = read.csv("C:/Users/gevab/SAE OUTIL DEV/data_age_graph.csv", sep=";" , stringsAsFactors = FALSE)

donnees$code_insee <- as.character(donnees$code_insee)
donnees$code_insee <- ifelse(
  nchar(donnees$code_insee) == 4,
  paste0("0", donnees$code_insee),
  donnees$code_insee
)


# Puis filtrer 
surf_filtre <- SURF[SURF$COMMUNE %in% donnees$code_insee, ]
catl_filtre <- CATL[CATL$COMMUNE %in% donnees$code_insee, ]
typl_filtre <- TYPL[TYPL$COMMUNE %in% donnees$code_insee, ]
nbpi_filtre <- NBPI[NBPI$COMMUNE %in% donnees$code_insee, ]

# Aggregation
catl_agg <- catl_filtre %>%
  filter(CATL %in% c("1", "2", "3", "4", "Z")) %>%
  group_by(COMMUNE, CATL) %>%
  summarise(Nombre_de_logements = n()) %>%
  ungroup() %>%
  mutate(Categorie = recode(CATL,
                            "1" = "Résidences principales",
                            "2" = "Logements occasionnels",
                            "3" = "Résidences secondaires",
                            "4" = "Logements vacants",
                            "Z" = "Hors logement ordinaire"))

###
typl_agg <- TYPL %>%
  filter(TYPL %in% c("1", "2", "3", "4", "5", "6", "Z")) %>%
  group_by(COMMUNE, TYPL) %>%
  summarise(Nombre_de_logements = n()) %>%
  ungroup() %>%
  mutate(Type = recode(TYPL,
                       "1" = "Maison",
                       "2" = "Appartement",
                       "3" = "Logement-foyer",
                       "4" = "Chambre d'hôtel",
                       "5" = "Habitation de fortune",
                       "6" = "Pièce indépendante",
                       "Z" = "Hors logement ordinaire"))

###
surface_labels <- c(
  "1" = "Moins de 30 m²",
  "2" = "De 30 à moins de 40 m²",
  "3" = "De 40 à moins de 60 m²",
  "4" = "De 60 à moins de 80 m²",
  "5" = "De 80 à moins de 100 m²",
  "6" = "De 100 à moins de 120 m²",
  "7" = "120 m² ou plus",
  "Y" = "Hors résidence principale",
  "Z" = "Hors logement ordinaire"
)

surf_agg <- SURF %>%
  group_by(COMMUNE, SURF) %>%
  summarise(Nombre_de_logements = n()) %>%
  ungroup() %>%
  mutate(Superficie = recode(SURF, !!!surface_labels)) %>%
  filter(!is.na(Superficie))

###
piece_labels <- c(setNames(
  sprintf("%d pièce%s", 1:19, ifelse(1:19 > 1, "s", "")),
  sprintf("%02d", 1:19)
),
"20" = "20 pièces et plus",
"YY" = "Hors résidence principale",
"ZZ" = "Hors logement ordinaire"
)

nbpi_agg <- NBPI %>%
  group_by(COMMUNE, NBPI) %>%
  summarise(Nombre_de_logements = n()) %>%
  ungroup() %>%
  mutate(Nombre_de_pieces = recode(NBPI, !!!piece_labels)) %>%
  filter(!is.na(Nombre_de_pieces))

# Export
write.csv(surf_agg, "C:/Users/gevab/SAE OUTIL DEV/df_SURF.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(catl_agg, "C:/Users/gevab/SAE OUTIL DEV/df_CATL.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(nbpi_agg, "C:/Users/gevab/SAE OUTIL DEV/df_NBPI.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(typl_agg, "C:/Users/gevab/SAE OUTIL DEV/df_TYPL.csv", row.names = FALSE, fileEncoding = "UTF-8")
