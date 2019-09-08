package com.mazhara.utils.corenlp;

import java.util.ArrayList;
import java.util.List;

public class SentimentTransformer {

    public SentimentValues getSentiment(String text){

        SentimentAnalyzer sentimentAnalyzer = new SentimentAnalyzer();
        sentimentAnalyzer.initialize();
        SentimentResult sentimentResult = sentimentAnalyzer.getSentimentResult(text);
        List<Object> list = new ArrayList<Object>();

        return new SentimentValues(sentimentResult.getSentimentScore(),sentimentResult.getSentimentType());

    }

     public class SentimentValues{

        public int sentimentScore;
        public String sentimentType;

        public SentimentValues(int sentimentScore, String sentimentType){
            this.sentimentScore = sentimentScore;
            this.sentimentType = sentimentType;
        }

         public int getSentimentScore() {
            return sentimentScore;
        }

         public void setSentimentScore(int sentimentScore) {
            this.sentimentScore = sentimentScore;
        }

         public String getSentimentType() {
            return sentimentType;
        }

         public void setSentimentType(String sentimentType) {
            this.sentimentType = sentimentType;
        }
    }

}
