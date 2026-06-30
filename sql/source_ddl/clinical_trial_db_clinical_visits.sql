DROP TABLE IF EXISTS `clinical_visits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clinical_visits` (
  `visit_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `investigator_id` int NOT NULL,
  `visit_number` int DEFAULT NULL,
  `visit_name` varchar(100) DEFAULT NULL,
  `visit_type` varchar(50) DEFAULT 'Scheduled',
  `scheduled_date` date DEFAULT NULL,
  `actual_visit_date` date DEFAULT NULL,
  `visit_window_start` date DEFAULT NULL,
  `visit_window_end` date DEFAULT NULL,
  `visit_status` varchar(30) DEFAULT 'Completed',
  `notes` varchar(1000) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`visit_id`),
  KEY `enrollment_id` (`enrollment_id`),
  KEY `investigator_id` (`investigator_id`),
  CONSTRAINT `clinical_visits_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `clinical_visits_ibfk_2` FOREIGN KEY (`investigator_id`) REFERENCES `investigators` (`investigator_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
