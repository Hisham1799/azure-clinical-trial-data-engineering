DROP TABLE IF EXISTS `protocol_deviations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `protocol_deviations` (
  `deviation_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `enrollment_id` int NOT NULL,
  `visit_id` int DEFAULT NULL,
  `reported_by_investigator_id` int NOT NULL,
  `deviation_category` varchar(100) DEFAULT NULL,
  `deviation_description` varchar(1000) DEFAULT NULL,
  `protocol_section` varchar(100) DEFAULT NULL,
  `deviation_date` date DEFAULT NULL,
  `impact_on_patient` varchar(300) DEFAULT NULL,
  `corrective_action` varchar(500) DEFAULT NULL,
  `is_major` tinyint(1) DEFAULT '0',
  `reported_to_irb` tinyint(1) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`deviation_id`),
  KEY `patient_id` (`patient_id`),
  KEY `enrollment_id` (`enrollment_id`),
  KEY `visit_id` (`visit_id`),
  KEY `reported_by_investigator_id` (`reported_by_investigator_id`),
  CONSTRAINT `protocol_deviations_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `protocol_deviations_ibfk_2` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `protocol_deviations_ibfk_3` FOREIGN KEY (`visit_id`) REFERENCES `clinical_visits` (`visit_id`),
  CONSTRAINT `protocol_deviations_ibfk_4` FOREIGN KEY (`reported_by_investigator_id`) REFERENCES `investigators` (`investigator_id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
