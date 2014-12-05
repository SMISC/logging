<?php

class ScoresController extends BaseController
{
    public function showTeamList()
    {
        $redis = LaravelRedis::connection('pacsocial');

        $this->layout->content = View::make('scores.list')->with(array(
            'info' => $redis->llen('info'),
            'followers' => $redis->llen('followers'),
            'tweets' => $redis->llen('tweets')
        ));
    }
}
