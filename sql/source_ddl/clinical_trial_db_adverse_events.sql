DROP TABLE IF EXISTS `adverse_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `adverse_events` (
  `ae_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `visit_id` int NOT NULL,
  `enrollment_id` int NOT NULL,
  `reporter_investigator_id` int NOT NULL,
  `ae_term` varchar(300) DEFAULT NULL,
  `meddra_pt_code` varchar(20) DEFAULT NULL,
  `severity` varchar(30) DEFAULT NULL,
  `ctcae_grade` int DEFAULT NULL,
  `onset_date` date DEFAULT NULL,
  `resolution_date` date DEFAULT NULL,
  `outcome` varchar(50) DEFAULT NULL,
  `is_serious` tinyint(1) DEFAULT '0',
  `sae_category` varchar(100) DEFAULT NULL,
  `causality` varchar(50) DEFAULT NULL,
  `action_taken` varchar(100) DEFAULT NULL,
  `is_expected` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ae_id`),
  KEY `patient_id` (`patient_id`),
  KEY `visit_id` (`visit_id`),
  KEY `enrollment_id` (`enrollment_id`),
  KEY `reporter_investigator_id` (`reporter_investigator_id`),
  CONSTRAINT `adverse_events_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `adverse_events_ibfk_2` FOREIGN KEY (`visit_id`) REFERENCES `clinical_visits` (`visit_id`),
  CONSTRAINT `adverse_events_ibfk_3` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `adverse_events_ibfk_4` FOREIGN KEY (`reporter_investigator_id`) REFERENCES `investigators` (`investigator_id`)
) ENGINE=InnoDB AUTO_INCREMENT=246 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
