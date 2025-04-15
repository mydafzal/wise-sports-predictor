import os
import json
from datetime import datetime
from typing import Dict, List
from WiseSportsAI_NBA.components.teamstats import update_all_teams
from WiseSportsAI_NBA.logging import logger

class TeamStatsPipeline:
    def __init__(self):
        self.team_stats_config = {
            'base_dir': "Artifacts/TeamStats",
            'team_mapping_file': "Artifacts/TeamInfo/team_mapping.csv"
        }

    def run_pipeline(self):
        try:
            logger.info("Team Stats Pipeline Started")
            
            # Ensure directories exist
            os.makedirs(self.team_stats_config['base_dir'], exist_ok=True)
            os.makedirs(os.path.dirname(self.team_stats_config['team_mapping_file']), exist_ok=True)
            
            # Update all team stats
            success = update_all_teams()
            
            if not success:
                raise Exception("Failed to update team stats")
            
            logger.info("Team Stats Pipeline Completed")
            return {"status": "success", "message": "Team stats updated successfully"}
            
        except Exception as e:
            logger.exception(e)
            raise e

if __name__ == '__main__':
    try:
        pipeline = TeamStatsPipeline()
        pipeline.run_pipeline()
    except Exception as e:
        logger.exception(e)
        raise e