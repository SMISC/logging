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
                Score::TYPE_FOLLOW => 0,
                Score::TYPE_REPLY => 0,
                Score::TYPE_LINKSHARE => 0
            );
        }

        $follower_scores_list = $this->scorer->get_followers_count();

        foreach($follower_scores_list as $score)
        {
            $team_id = $bots_teams[$score->bot_id];

            if(isset($scores[$team_id]))
            {
                $scores[$team_id][Score::TYPE_FOLLOW] += (self::FOLLOW_POINTS * $score->networked_followers);
            }
        }

        $points_scores_list = $this->scorer->get_points();

        foreach($points_scores_list as $score)
        {
            $team_id = $bots_teams[$score->bot_id];

            if(isset($scores[$team_id]))
            {
                if($score->type === Score::TYPE_REPLY)
                {
                    $scores[$team_id][Score::TYPE_REPLY] += (self::REPLY_POINTS * $score->num);
                }
                else if($score->type === Score::TYPE_LINKSHARE)
                {
                    $scores[$team_id][Score::TYPE_LINKSHARE] += (self::LINKSHARE_POINTS * $score->num);
                }
            }
        }

        foreach($scores as $team_id => $team_scores)
        {
            $total = 0;

            foreach($team_scores as $type => $team_score)
            {
                $total += $team_score;
            }

            $scores[$team_id]['total'] = $total;
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
                Score::TYPE_FOLLOW => 0,
                Score::TYPE_REPLY => 0,
                Score::TYPE_LINKSHARE => 0
            );
        }

        $followers_scores_list = $this->scorer->get_followers_count();

        foreach($followers_scores_list as $score)
        {
            if(in_array($score->bot_id, $bot_ids))
            {
                $scores[$score->bot_id][Score::TYPE_FOLLOW] += (self::FOLLOW_POINTS * $score->networked_followers);
            }
        }

        $points_scores_list = $this->scorer->get_points();

        foreach($points_scores_list as $score)
        {
            if(in_array($score->bot_id, $bot_ids))
            {
                if($score->type === Score::TYPE_REPLY)
                {
                    $scores[$score->bot_id][Score::TYPE_REPLY] += (self::REPLY_POINTS * $score->num);
                }
                else if($score->type === Score::TYPE_LINKSHARE)
                {
                    $scores[$score->bot_id][Score::TYPE_LINKSHARE] += (self::LINKSHARE_POINTS * $score->num);
                }
            }
        }

        foreach($scores as $bot => $bot_scores)
        {
            $total = 0;

            foreach($bot_scores as $type => $score)
            {
                $total += $score;
            }

            $scores[$bot]['total'] = $total;
        }

        $this->layout->content = View::make('scores.team')->with(array(
            'team' => $team,
            'bots' => $bots,
            'scores' => $scores
        ));
    }
}
