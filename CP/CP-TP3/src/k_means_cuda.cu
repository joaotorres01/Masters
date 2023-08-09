#include <stdio.h>
#include <cuda.h>
#include <cuda_runtime.h>
#include <linux/kernel.h>
#include <time.h>

clock_t start, end;
double cpu_time_used;

#define N 10000000
#define K 16
#define NUM_THREADS_PER_BLOCK 256

float *points_x;
float *points_y;
int *cluster;

float *centroid_x;
float *centroid_y;

float *newCentroid_x;
float *newCentroid_y;

int *size;

int iterations = 0;

float *d_centroid_x, *d_centroid_y, *d_points_x, *d_points_y;
int *d_cluster;

// __device__ static inline float distance(float p1_x, float p1_y, float p2_x, float p2_y) {
//     //No need for the actual value of the distance. We can avoid the sqrt() function since we'll only be comparing which one is the shortest distance.
//     return ((p2_x - p1_x)*(p2_x - p1_x)) + ((p2_y - p1_y)*(p2_y - p1_y));
// }

void initialize(){
    points_x = (float *)malloc(N * sizeof(float));
    points_y = (float *)malloc(N * sizeof(float));
    cluster = (int *)malloc(N * sizeof(int));

    centroid_x = (float *)malloc(K * sizeof(float));
    centroid_y = (float *)malloc(K * sizeof(float));

    newCentroid_x = (float *)malloc(K * sizeof(float));
    newCentroid_y = (float *)malloc(K * sizeof(float));
    size = (int *)malloc(K * sizeof(int));

    cudaMalloc(&d_centroid_x, K*sizeof(float));
    cudaMalloc(&d_centroid_y, K*sizeof(float));
    cudaMalloc(&d_points_x, N*sizeof(float));
    cudaMalloc(&d_points_y, N*sizeof(float));
    cudaMalloc(&d_cluster, N*sizeof(int));

    srand(10);
// Random values for the points
    for (int i = 0; i < N; i++){
	points_x[i] = (float)rand() / RAND_MAX;
	points_y[i] = (float)rand() / RAND_MAX;
    }
    for (int i = 0; i < K; i++){
	centroid_x[i] = points_x[i];
	centroid_y[i] = points_y[i];
    }

    cudaMemcpy(d_centroid_x, centroid_x, K*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_centroid_y, centroid_y, K*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_points_x, points_x, N*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_points_y, points_y, N*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_cluster, cluster, N*sizeof(int), cudaMemcpyHostToDevice);
}

__global__ void kernel_computeDistances (float *d_centroid_x, float *d_centroid_y, float *d_points_x, float *d_points_y, int *d_cluster) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
	float smallerDist = ((d_points_x[i] - d_centroid_x[0]) * (d_points_x[i] - d_centroid_x[0])) + ((d_points_y[i] - d_centroid_y[0]) * (d_points_y[i] - d_centroid_y[0]));
	int clusterIndex = 0;
	for (int j = 1; j < K; j++){
	    float tempDist = ((d_points_x[i] - d_centroid_x[j]) * (d_points_x[i] - d_centroid_x[j])) + ((d_points_y[i] - d_centroid_y[j]) * (d_points_y[i] - d_centroid_y[j]));
	    clusterIndex = tempDist < smallerDist ? j : clusterIndex;
	    smallerDist = tempDist < smallerDist ? tempDist : smallerDist;
	}
	//Stores cluster index associated to each point
	d_cluster[i] = clusterIndex;
    }
}

void k_means(){
    for(iterations = 0; iterations < 20; iterations++) {
	// Each iteration resets every cluster
	for (int i = 0; i < K; i++){
	    size[i] = 0;
	    newCentroid_x[i] = 0.0;
	    newCentroid_y[i] = 0.0;
	}
    int blocks = (N + NUM_THREADS_PER_BLOCK - 1) / NUM_THREADS_PER_BLOCK;
	kernel_computeDistances<<<blocks, NUM_THREADS_PER_BLOCK>>>(d_centroid_x, d_centroid_y, d_points_x, d_points_y, d_cluster);
	cudaDeviceSynchronize();
	 cudaError_t err = cudaGetLastError();
	 if (err != cudaSuccess)
        {
            printf("1 -> Kernel launch failed: %s\n", cudaGetErrorString(err));
            return;
        }
        cudaMemcpy(centroid_x, d_centroid_x, K*sizeof(float), cudaMemcpyDeviceToHost);
        cudaMemcpy(centroid_y, d_centroid_y, K*sizeof(float), cudaMemcpyDeviceToHost);
        cudaMemcpy(points_x, d_points_x, N*sizeof(float), cudaMemcpyDeviceToHost);
        cudaMemcpy(points_y, d_points_y, N*sizeof(float), cudaMemcpyDeviceToHost);
        cudaMemcpy(cluster, d_cluster, N*sizeof(int), cudaMemcpyDeviceToHost);

        for (int i = 0; i < N; i++) {
            // Sums the value of the point to the newCentroid variable.
            size[cluster[i]]++;
            newCentroid_x[cluster[i]] += points_x[i];
            newCentroid_y[cluster[i]] += points_y[i];
        }

    // Checks if the newCentroid is the same as the current centroid (stopping case).
    // Sets the current centroid to the value of the newCentroid.
    for (int i = 0; i < K; i++){
        newCentroid_x[i] /= size[i];
        newCentroid_y[i] /= size[i];
        centroid_x[i] = newCentroid_x[i];
        centroid_y[i] = newCentroid_y[i];
    }

    cudaMemcpy(d_centroid_x, centroid_x, K*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_centroid_y, centroid_y, K*sizeof(float), cudaMemcpyHostToDevice);

    }
}

static inline void printEndMessage(){
    printf("\nN: %d, K = %d\n", N, K);
    for (int i = 0; i < K; i++){
        printf("Center: (%.3f, %.3f) : size: %d\n", centroid_x[i], centroid_y[i], size[i]);
    }
    printf("Iterations: %d\n", iterations);
}

int main(int argc, char *argv[]){
    start = clock();
    initialize();
    k_means();
    end = clock();
    printEndMessage();
    printf("Work took %f seconds\n", end - start / CLOCKS_PER_SEC);
    return 0;
}