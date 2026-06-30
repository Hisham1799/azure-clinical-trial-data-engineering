DROP TABLE IF EXISTS `dropouts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dropouts` (
  `dropout_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `enrollment_id` int NOT NULL,
  `withdrawal_date` date DEFAULT NULL,
  `withdrawal_reason` varchar(100) DEFAULT NULL,
  `withdrawal_reason_detail` varchar(500) DEFAULT NULL,
  `last_visit_id` int DEFAULT NULL,
  `was_replaced` tinyint(1) DEFAULT '0',
  `lost_to_followup` tinyint(1) DEFAULT '0',
  `death_flag` tinyint(1) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dropout_id`),
  KEY `patient_id` (`patient_id`),
  KEY `enrollment_id` (`enrollment_id`),
  KEY `last_visit_id` (`last_visit_id`),
  CONSTRAINT `dropouts_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `dropouts_ibfk_2` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `dropouts_ibfk_3` FOREIGN KEY (`last_visit_id`) REFERENCES `clinical_visits` (`visit_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
