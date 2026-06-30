DROP TABLE IF EXISTS `clinical_studies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clinical_studies` (
  `study_id` int NOT NULL AUTO_INCREMENT,
  `study_code` varchar(20) NOT NULL,
  `study_title` varchar(500) NOT NULL,
  `therapeutic_area` varchar(100) DEFAULT NULL,
  `phase` varchar(10) DEFAULT NULL,
  `sponsor_name` varchar(200) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Active',
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `target_enrollment` int DEFAULT NULL,
  `actual_enrollment` int DEFAULT '0',
  `primary_endpoint` varchar(500) DEFAULT NULL,
  `blinding_type` varchar(50) DEFAULT NULL,
  `randomization_ratio` varchar(20) DEFAULT NULL,
  `irb_approval_number` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`study_id`),
  UNIQUE KEY `study_code` (`study_code`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
