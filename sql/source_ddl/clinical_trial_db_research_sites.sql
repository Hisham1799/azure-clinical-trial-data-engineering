DROP TABLE IF EXISTS `research_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `research_sites` (
  `site_id` int NOT NULL AUTO_INCREMENT,
  `site_code` varchar(20) NOT NULL,
  `site_name` varchar(200) NOT NULL,
  `country` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `site_type` varchar(50) DEFAULT NULL,
  `contact_name` varchar(150) DEFAULT NULL,
  `contact_email` varchar(150) DEFAULT NULL,
  `contact_phone` varchar(30) DEFAULT NULL,
  `activation_date` date DEFAULT NULL,
  `status` varchar(30) DEFAULT 'Active',
  `max_patient_capacity` int DEFAULT '50',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`site_id`),
  UNIQUE KEY `site_code` (`site_code`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
