<?php

class DiagnosticsController extends BaseController
{
    const TARGET_SIZE = 15000;

    public function showOverview()
    {
        $redis = LaravelRedis::connection('pacsocial');

        $snapshots = array(
            array(
                'redis_key' => 'info',
                'name' => 'Profiles',
                'target_size' => self::TARGET_SIZE 
            ),
            array(
                'redis_key' => 'followers_wide',
                'name' => 'Followers (long)',
                'target_size' => self::TARGET_SIZE 
            ),
            array(
                'redis_key' => 'followers_bot',
                'name' => 'Followers (legacy short)',
                'target_size' => 'n/a'
            ),
            array(
                'redis_key' => 'followers_bot_v2',
                'name' => 'Followers (legacy short)',
                'target_size' => 'n/a'
            ),
            /*
            array(
                'redis_key' => 'followers',
                'name' => 'Followers (legacy)',
                'target_size' => self::TARGET_SIZE
            ),
            */

            array(
                'redis_key' => 'tweets',
                'name' => 'Tweets',
                'target_size' => self::TARGET_SIZE 
            )
        );

        foreach($snapshots as &$snapshot)
        {
            $snapshot['length'] = $redis->llen($snapshot['redis_key']);
            $snapshot['count'] = count(Scan::whereRaw('type = ? and ref_end is not NULL', array($snapshot['redis_key']))->get());
            $snapshot['in_progress'] = Scan::whereRaw('type = ? and ref_end is NULL', array($snapshot['redis_key']))->orderBy('id', 'desc')->limit(1)->get();
            $snapshot['last_finished'] = Scan::whereRaw('type = ? and ref_end is not NULL', array($snapshot['redis_key']))->orderBy('id', 'desc')->limit(1)->get();
        }

        $backups = Backup::with('scan')->get();

        $backups_by_type = array();

        foreach($backups as $backup)
        {
            $type = $backup->scan->type;

            if(!isset($backups_by_type[$type])) {
                $backups_by_type[$type] = 0;
            }

            $backups_by_type[$type] += 1;
        }

        $this->layout->content = View::make('diagnostics.overview')->with(array(
            'snapshots' => $snapshots,
            'backups' => $backups_by_type
        ));
    }
}
