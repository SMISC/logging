<?php

class Score
{
    const TYPE_FOLLOW = 'follow';
    const TYPE_REPLY = 'reply';
    const TYPE_LINKSHARE = 'link';

    public function get_followers_count()
    {
        return DB::connection('competition')->select('select team_bot.twitter_id as bot_id, (select count(distinct from_user) as networked_followers from tuser_tuser_bot inner join targets on targets.twitter_id = tuser_tuser_bot.from_user where to_user = team_bot.twitter_id) as networked_followers from team_bot');
    }

    public function get_points()
    {
        $rv = DB::connection('competition')->select('select bot_id, type, count(*) as num from point group by type, bot_id');

        foreach($rv as $val)
        {
            // facepalm
            $val->type = trim($val->type);
        }

        return $rv;
    }
}
