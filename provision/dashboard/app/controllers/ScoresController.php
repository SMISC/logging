<?php

class ScoresController extends BaseController
{
    const FOLLOW_POINTS = 1;
    const REPLY_POINTS = 3;
    const LINKSHARE_POINTS = 5;

    public function __construct(Score $scorer)
    {
        $this->scorer = $scorer;
    }

    public function showTeams()
    {
        $teams = Team::all();

        $bots = array();
        $scores = array();
        $bots_teams = array();

        foreach($teams as $team)
        {
            $bots[$team->id] = $team->bots->toArray();

            foreach($bots[$team->id] as $bot)
            {
                $bots_teams[$bot['twitter_id']] = $bot['team_id'];
            }

            $scores[$team->id] = array(
                'followers' => 0
            );
        }

        $scores_list = $this->scorer->get_followers_count();

        foreach($scores_list as $score)
        {
            $team_id = $bots_teams[$score->bot_id];

            if(isset($scores[$team_id]))
            {
                $scores[$team_id]['followers'] += (self::FOLLOW_POINTS * $score->networked_followers);
            }
        }

        $this->layout->content = View::make('scores.teams')->with(array(
            'teams' => $teams,
            'bots' => $bots,
            'scores' => $scores
        ));
    }

    public function showTeam($team_id)
    {
        $team = Team::find($team_id);
        $bots = $team->bots->toArray();

        $scores = array();

        $bot_ids = array();

        foreach($bots as $bot)
        {
            $bot_ids[] = $bot['twitter_id'];

            $scores[$bot['twitter_id']] = array(
                'followers' => 0
            );
        }

        $scores_list = $this->scorer->get_followers_count();

        foreach($scores_list as $score)
        {
            if(in_array($score->bot_id, $bot_ids))
            {
                $scores[$score->bot_id]['followers'] += (self::FOLLOW_POINTS * $score->networked_followers);
            }
        }

        $this->layout->content = View::make('scores.team')->with(array(
            'team' => $team,
            'bots' => $bots,
            'scores' => $scores
        ));
    }
}
