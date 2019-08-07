package com.mazhara.utils.apps;
import com.mazhara.utils.postre.PostgresUtils;
import com.mazhara.utils.twitter.TwitterUtils;
import twitter4j.Twitter;
import twitter4j.TwitterFactory;
import java.sql.Connection;
import java.util.List;


public class TwitterApp {

    public static void main(String[] args){

        Twitter twitter = new TwitterFactory(TwitterUtils.getConfigs()).getInstance();

        String user = System.getenv("TWITTER_USER");
        System.out.println(user);

        Connection connection = PostgresUtils.connectToPostgres();

        PostgresUtils.createReplyTable(connection, user);

        List<Long> friends =  TwitterUtils.getUsersFriendsIds(twitter, user);

        for (Long friend: friends){
            TwitterUtils.storeUserTweets(twitter, friend, 100, user, connection);
        }

    }

}
