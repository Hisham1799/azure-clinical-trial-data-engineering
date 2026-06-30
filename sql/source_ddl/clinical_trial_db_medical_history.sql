DROP TABLE IF EXISTS `medical_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_history` (
  `history_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `condition_name` varchar(300) DEFAULT NULL,
  `icd10_code` varchar(20) DEFAULT NULL,
  `onset_year` int DEFAULT NULL,
  `resolution_year` int DEFAULT NULL,
  `is_ongoing` tinyint(1) DEFAULT '1',
  `severity` varchar(30) DEFAULT NULL,
  `treatment` varchar(300) DEFAULT NULL,
  `notes` varchar(500) DEFAULT NULL,
  `recorded_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`history_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `medical_history_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`)
) ENGINE=InnoDB AUTO_INCREMENT=315 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
