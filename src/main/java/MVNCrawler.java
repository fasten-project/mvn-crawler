/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


import java.io.BufferedReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.parser.Parser;
import org.jsoup.select.Elements;


/**
 * A simple crawler to fetch metadata of projects from Maven repositories.
 * It generates a CSV file with following fields:
 * - Project name
 * - Group ID
 * - Artifact ID
 * - Version
 * - Timestamp
 */


public class MVNCrawler {

    private String csvFileName;
    public String mvnRepo = "http://repo2.maven.apache.org/maven2/";

    static class POMFile{
        /**
         * It represents a POM file with its timestamp
         */
        public String fileName;
        public String date;
        public String time;

        POMFile(final String fileName, final String date, final String time){
            this.fileName = fileName;
            this.date = date;
            this.time = time;
        }
    }

    static class MVNProject{
        /**
         * It encapsulates a project on the Maven repository.
         */

        public String projectName;
        public String groupID;
        public String artifactID;
        public String version;
        public String timestamp;

        public MVNProject(String projectName, String groupID, String artifactID, String version, String timestamp) {
            this.projectName = projectName;
            this.groupID = groupID;
            this.artifactID = artifactID;
            this.version = version;
            this.timestamp = timestamp;
        }

//        public String getProjectName() {
//            return projectName;
//        }
//
//        public String getGroupID() {
//            return groupID;
//        }
//
//        public String getArtifactID() {
//            return artifactID;
//        }
//
//        public String getVersion() {
//            return version;
//        }
//
//        public String getTimestamp() {
//            return timestamp;
//        }
//
//        public void setProjectName(String projectName) {
//            this.projectName = projectName;
//        }
//
//        public void setGroupID(String groupID) {
//            this.groupID = groupID;
//        }
//
//        public void setArtifactID(String artifactID) {
//            this.artifactID = artifactID;
//        }
//
//        public void setVersion(String version) {
//            this.version = version;
//        }
//
//        public void setTimestamp(String timestamp) {
//            this.timestamp = timestamp;
//        }
    }

    public MVNCrawler(final String csvFileName){
        this.csvFileName = csvFileName;
    }

    public void startCrawler() throws IOException, InterruptedException {
        HashSet<String> pomFiles =  this.findPOMFiles(this.mvnRepo, new HashSet<String>());

        System.out.println("Finished...");
        for(String f: pomFiles) System.out.println(f);

        savePOMFiles("pomFiles.txt", pomFiles);

        //List<MVNProject> extractedProjects = this.extractMVNProjects(this.getPOMFiles());
        //this.projectsToCSV(extractedProjects);
    }

    private static void savePOMFiles(String fileName, HashSet<String> pomFiles) throws IOException {
        FileWriter f = new FileWriter(fileName);
        for(String pf : pomFiles){
            f.write(pf + System.lineSeparator());
        }
        f.close();
    }

    private static boolean isURLFile(String URL) throws URISyntaxException {
        /**
         * A utility method to check whether a URL is a file or not.
         */

        URI uri = new URI(URL);
        String[] urlSegments = uri.getPath().split("/");
        String lastSeg = urlSegments[urlSegments.length - 1];

        return lastSeg.matches(".+\\.\\w+");

    }

    private HashSet<String> findPOMFiles(String URL, HashSet<String> pomFiles, int cooldown) throws IOException, InterruptedException {
        /**
         * Finds all the POM files in given Maven repos recursively.
         */

        HashSet<String> links = new HashSet<>(); // Keeps track of links

        if(!links.contains(URL)){

            try {
                // Checks whether link is a valid dir
                if (!isURLFile(URL)){
                    links.add(URL);

                    // Wait up to specified time for avoiding blocking the IP
                    Thread.sleep(1000 * cooldown);

                    Document doc = Jsoup.connect(URL).get();
                    Elements linksOnPage = doc.select("a[href]");

                    //int i = 0;
                    for (Element link : linksOnPage) {
                        // Excludes up level dirs (e.g. ../)

                        //if(i <= 10){
                        if(!link.text().matches("\\.\\./")){
                            System.out.println(link.attr("abs:href"));
                            findPOMFiles(link.attr("abs:href"), pomFiles, cooldown);
                            //}
                        } else break;

                        //i++;
                    }

                } else if (URL.matches(".+\\.pom")) {
                    pomFiles.add(URL);
                    System.out.println("Found a pom file: " + URL);
                }
            } catch (IOException | URISyntaxException e) {
                System.out.println("For '" + URL + "': " + e.getMessage());
            }
        }

        return pomFiles;
    }

    // TODO: It doesn't get all the POM Files, there are rare cases... hierarchy of files might be deeper!
    private HashMap<String, HashMap<String, HashMap<String, POMFile>>> getPOMFiles() throws IOException {



        Document doc = Jsoup.connect(mvnRepo).get();
        Elements links = doc.getElementsByTag("a");

        HashMap<String, HashMap<String, HashMap<String, POMFile>>> authorRepos = new HashMap<>();

        // Regex patterns for extracting only repositories and their versions
        String namePattern = "\\w+/";
        String verPattern = ".+\\.\\w+";
        String pomFilePattern = ".+\\.pom";

        int i = 0;

        // Iterates through organizations or users
        for(Element author : links){
            String authorName = author.text();
            authorRepos.put(authorName, new HashMap<String, HashMap<String, POMFile>>());

            System.out.println("Author's" + authorName + "Repos:");
            if(authorName.matches(namePattern)){
                //System.out.println(repoName.substring(0, repoName.length() - 1));
                Document authorPage = Jsoup.connect(mvnRepo + authorName).get();
                Elements authorLinks = authorPage.getElementsByTag("a");

                // Iterates through repositories
                for(Element repo: authorLinks){
                    String repoName = repo.text();
                    authorRepos.get(authorName).put(repoName, new HashMap<String, POMFile>());

                    // "(?!\\.\\.)" pattern for excluding up level dirs (e.g. ../)
                    if(repoName.matches("(?!\\.\\.)" + namePattern)){
                        System.out.println(repoName);

                        Document repoPage = Jsoup.connect(mvnRepo + authorName + repoName).get();
                        Elements repoLinks = repoPage.getElementsByTag("a");

                        // Iterates through releases
                        for(Element ver: repoLinks){
                            String verNumber = ver.text();
                            //System.out.println(verNumber);

                            if(verNumber.matches("(?!\\.\\.).*") && !verNumber.matches(verPattern)){
                                System.out.println(verNumber);
                                System.out.println(mvnRepo + authorName + "/" + repoName + "/" + verNumber + "/");

                                Document verPage = Jsoup.connect(mvnRepo + authorName + repoName + verNumber).get();
                                Element content = verPage.getElementById("contents");

                                // Ignores releases without any files
                                if(content != null){
                                    Elements verLinks = verPage.getElementsByTag("a");
                                    //System.out.println(content.ownText());
                                    String timeStampList[] = content.ownText().split("\\r?\\n");

                                    int j = 0;
                                    // Iterates through files in a release
                                    for(Element file : verLinks){
                                        String fileName = file.text();
                                        if(fileName.matches(pomFilePattern)){
                                            // For separating timestamp and file size
                                            String[] timeStampSplit = timeStampList[j].trim().split("\\s+");
                                            authorRepos.get(authorName).get(repoName).put(verNumber, new POMFile(fileName, timeStampSplit[0], timeStampSplit[1]));
                                            break;
                                        }

                                        j++;
                                    }
                                }
                            }
                        }
                        }
                    }
                }

                System.out.println("--------------------------------");
                i++;
                if(i == 4) break;
            }
        return authorRepos;
        }

    public List<MVNProject> extractMVNProjects(HashMap<String, HashMap<String, HashMap<String, POMFile>>> POMFiles) throws IOException {

        List<MVNProject> projects = new ArrayList<>();

        for(String user : POMFiles.keySet()){

            for(String repo : POMFiles.get(user).keySet()) {

                for(HashMap.Entry<String, POMFile> verAndPOM : POMFiles.get(user).get(repo).entrySet()){
                    Document XMLDoc = Jsoup.parse(new URL(mvnRepo + user + repo + verAndPOM.getKey() + verAndPOM.getValue().fileName).openStream(),
                            "UTF-8", "", Parser.xmlParser());

                    String groupID = "";
                    String artifactID = "";

                    for(Element e: XMLDoc.getElementsByTag("project"))
                    {
                        groupID = e.getElementsByTag("groupId").text();
                        artifactID =  e.getElementsByTag("artifactId").text();

                        if(!groupID.isEmpty() && !artifactID.isEmpty()){
                            break;
                        }
                    }

                    MVNProject p = new MVNProject(repo.substring(0, repo.length()-1), groupID,
                            artifactID, verAndPOM.getKey().substring(0, verAndPOM.getKey().length()-1),
                            verAndPOM.getValue().date + " " + verAndPOM.getValue().time);
                    //System.out.println(p.projectName + p.groupID + p.artifactID + p.version + p.timestamp);
                    projects.add(p);
                }
            }
        }

        return projects;
    }

    public void projectsToCSV(List<MVNProject> projects) throws IOException {

        String[] headerNames = {"projectName", "groupID", "artifactID", "version", "timestamp"};

        FileWriter csvFile = new FileWriter(this.csvFileName);
        CSVPrinter csv = new CSVPrinter(csvFile, CSVFormat.DEFAULT.withHeader(headerNames));

        for(MVNProject p : projects){
            csv.printRecord(p.projectName, p.groupID, p.artifactID, p.version, p.timestamp);
        }

        csvFile.close();
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        MVNCrawler crawler =  new MVNCrawler("mvn_repo.csv");
        crawler.startCrawler();
    }



}
