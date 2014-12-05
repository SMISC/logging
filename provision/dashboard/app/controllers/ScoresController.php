<?php

class ScoresController extends BaseController
{
    public function showTeamList()
    {
        $teams = Team::all();

        $bots = array();

        foreach($teams as $team)
        {
            $bots[$team->id] = count($team->bots);
        }

        $this->layout->content = View::make('scores.teams')->with(array(
            'teams' => $teams,
            'bots' => $bots
        ));
    }

    public function showTeam($team_id)
    {
        $team = Team::get($team_id);
        $bots = $team->bots;

        $this->layout->content = View::make('scores.team')->with(array(
            'team' => $team,
            'bots' => $bots
        ));
    }
}
