DROP TABLE IF EXISTS `study_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `study_sites` (
  `study_site_id` int NOT NULL AUTO_INCREMENT,
  `study_id` int NOT NULL,
  `site_id` int NOT NULL,
  `principal_investigator_id` int NOT NULL,
  `site_activation_date` date DEFAULT NULL,
  `site_close_date` date DEFAULT NULL,
  `enrolled_count` int DEFAULT '0',
  `status` varchar(30) DEFAULT 'Enrolling',
  PRIMARY KEY (`study_site_id`),
  KEY `study_id` (`study_id`),
  KEY `site_id` (`site_id`),
  KEY `principal_investigator_id` (`principal_investigator_id`),
  CONSTRAINT `study_sites_ibfk_1` FOREIGN KEY (`study_id`) REFERENCES `clinical_studies` (`study_id`),
  CONSTRAINT `study_sites_ibfk_2` FOREIGN KEY (`site_id`) REFERENCES `research_sites` (`site_id`),
  CONSTRAINT `study_sites_ibfk_3` FOREIGN KEY (`principal_investigator_id`) REFERENCES `investigators` (`investigator_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
