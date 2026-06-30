DROP TABLE IF EXISTS `concomitant_medications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `concomitant_medications` (
  `conmed_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `enrollment_id` int NOT NULL,
  `medication_id` int DEFAULT NULL,
  `drug_name_verbatim` varchar(200) DEFAULT NULL,
  `dose` varchar(100) DEFAULT NULL,
  `frequency` varchar(50) DEFAULT NULL,
  `route` varchar(50) DEFAULT NULL,
  `indication` varchar(300) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `is_ongoing` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`conmed_id`),
  KEY `patient_id` (`patient_id`),
  KEY `enrollment_id` (`enrollment_id`),
  KEY `medication_id` (`medication_id`),
  CONSTRAINT `concomitant_medications_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `concomitant_medications_ibfk_2` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `concomitant_medications_ibfk_3` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`medication_id`)
) ENGINE=InnoDB AUTO_INCREMENT=411 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
