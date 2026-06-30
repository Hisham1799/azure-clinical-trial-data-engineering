DROP TABLE IF EXISTS `questionnaires`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questionnaires` (
  `questionnaire_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `visit_id` int NOT NULL,
  `instrument_name` varchar(100) DEFAULT NULL,
  `instrument_version` varchar(20) DEFAULT NULL,
  `administration_date` date DEFAULT NULL,
  `ecog_score` int DEFAULT NULL,
  `global_health_score` decimal(5,2) DEFAULT NULL,
  `physical_functioning` decimal(5,2) DEFAULT NULL,
  `emotional_functioning` decimal(5,2) DEFAULT NULL,
  `fatigue_score` decimal(5,2) DEFAULT NULL,
  `pain_score` decimal(5,2) DEFAULT NULL,
  `completed_by` varchar(30) DEFAULT 'Patient',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`questionnaire_id`),
  KEY `patient_id` (`patient_id`),
  KEY `visit_id` (`visit_id`),
  CONSTRAINT `questionnaires_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `questionnaires_ibfk_2` FOREIGN KEY (`visit_id`) REFERENCES `clinical_visits` (`visit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=786 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
