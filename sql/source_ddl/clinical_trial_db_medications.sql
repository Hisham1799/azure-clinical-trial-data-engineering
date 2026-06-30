DROP TABLE IF EXISTS `medications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medications` (
  `medication_id` int NOT NULL AUTO_INCREMENT,
  `drug_name` varchar(200) NOT NULL,
  `brand_name` varchar(200) DEFAULT NULL,
  `drug_code` varchar(50) DEFAULT NULL,
  `drug_class` varchar(150) DEFAULT NULL,
  `route_of_admin` varchar(50) DEFAULT NULL,
  `formulation` varchar(100) DEFAULT NULL,
  `strength_unit` varchar(30) DEFAULT NULL,
  `manufacturer` varchar(200) DEFAULT NULL,
  `is_investigational` tinyint(1) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`medication_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
